use std::{
    ffi::OsStr,
    fs::File,
    io::Read,
    mem::{size_of, zeroed},
    os::windows::{ffi::OsStrExt, io::{AsRawHandle, FromRawHandle, OwnedHandle}},
    path::Path,
    ptr,
    sync::Mutex,
};
use windows::{
    core::{PCWSTR, PWSTR},
    Win32::{
        Foundation::{HANDLE, BOOL, ERROR_INSUFFICIENT_BUFFER, HANDLE_FLAG_INHERIT, HANDLE_FLAGS, NO_ERROR, SetHandleInformation, WAIT_OBJECT_0, WAIT_TIMEOUT},
        NetworkManagement::IpHelper::{GetExtendedTcpTable, MIB_TCPTABLE_OWNER_PID, TCP_TABLE_OWNER_PID_LISTENER},
        Networking::WinSock::AF_INET,
        Security::SECURITY_ATTRIBUTES,
        System::{
            JobObjects::{AssignProcessToJobObject, CreateJobObjectW, IsProcessInJob, TerminateJobObject,
                JobObjectExtendedLimitInformation, SetInformationJobObject,
                JOBOBJECT_EXTENDED_LIMIT_INFORMATION, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE},
            Pipes::CreatePipe,
            Threading::{CreateProcessW, GetExitCodeProcess, OpenProcess, ResumeThread, TerminateProcess,
                WaitForSingleObject, CREATE_NO_WINDOW, CREATE_SUSPENDED, STARTF_USESTDHANDLES,
                PROCESS_INFORMATION, PROCESS_QUERY_LIMITED_INFORMATION, STARTUPINFOW},
        },
    },
};

fn wide(value: &OsStr) -> Vec<u16> {
    value.encode_wide().chain(Some(0)).collect()
}

fn handle(value: &OwnedHandle) -> HANDLE {
    HANDLE(value.as_raw_handle())
}

pub struct OwnedLauncher {
    // Closing the non-inherited job kills only this launcher's descendants,
    // including on desktop crash. No PID-based termination or process-name kill.
    job: OwnedHandle,
    process: OwnedHandle,
}

impl OwnedLauncher {
    pub fn spawn(root: &Path) -> Result<Self, String> {
        let python = root.join(".venv/Scripts/python.exe");
        let adapter = root.join("apps/desktop/launcher_adapter.py");
        if !python.is_file() {
            return Err("The local Python environment is missing. Prepare Jarvis with its existing launcher, then retry.".into());
        }
        // Windows paths cannot contain quotes. Both arguments are fixed files
        // beneath the validated repository, never supplied by web content.
        let application = wide(python.as_os_str());
        let mut command = wide(OsStr::new(&format!("\"{}\" -I -B \"{}\"", python.display(), adapter.display())));
        let directory = wide(root.as_os_str());
        unsafe {
            let job = CreateJobObjectW(None, PCWSTR::null()).map_err(|e| e.to_string())?;
            let job = OwnedHandle::from_raw_handle(job.0);
            let mut limits: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = zeroed();
            limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            SetInformationJobObject(
                handle(&job), JobObjectExtendedLimitInformation,
                &limits as *const _ as *const _, size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            ).map_err(|e| e.to_string())?;
            let mut startup: STARTUPINFOW = zeroed();
            startup.cb = size_of::<STARTUPINFOW>() as u32;
            let mut info: PROCESS_INFORMATION = zeroed();
            CreateProcessW(
                PCWSTR(application.as_ptr()), Some(PWSTR(command.as_mut_ptr())),
                None, None, false, CREATE_SUSPENDED | CREATE_NO_WINDOW,
                None, PCWSTR(directory.as_ptr()), &startup, &mut info,
            ).map_err(|e| format!("Could not start the existing Jarvis launcher: {e}"))?;
            let process = OwnedHandle::from_raw_handle(info.hProcess.0);
            let thread = OwnedHandle::from_raw_handle(info.hThread.0);
            if let Err(error) = AssignProcessToJobObject(handle(&job), handle(&process)) {
                // The child has never run and cannot have created descendants.
                let _ = TerminateProcess(handle(&process), 1);
                return Err(format!("Could not establish safe process ownership: {error}"));
            }
            if ResumeThread(handle(&thread)) == u32::MAX {
                return Err("Could not resume the owned launcher.".into());
            }
            Ok(Self { job, process })
        }
    }

    pub fn running(&self) -> bool {
        unsafe { WaitForSingleObject(handle(&self.process), 0) == WAIT_TIMEOUT }
    }

    pub fn owns_listener(&self) -> Result<bool, String> {
        let Some(pid) = listener_pid()? else { return Ok(false) };
        unsafe {
            let process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid)
                .map_err(|e| format!("Could not verify the listener owner: {e}"))?;
            let process = OwnedHandle::from_raw_handle(process.0);
            let mut owned = windows::core::BOOL::default();
            IsProcessInJob(handle(&process), Some(handle(&self.job)), &mut owned)
                .map_err(|e| e.to_string())?;
            Ok(owned.as_bool())
        }
    }
}

pub struct OwnedPreparation {
    // The job remains open after bootstrap exits so any Ollama child started
    // during preparation stays desktop-owned until this desktop exits.
    job: OwnedHandle,
    process: OwnedHandle,
    output: Mutex<File>,
}

impl OwnedPreparation {
    pub fn spawn(root: &Path, python: &Path) -> Result<Self, String> {
        let bootstrap = root.join("scripts/jarvis_bootstrap.py");
        if !bootstrap.is_file() {
            return Err("The repository bootstrap script is missing.".into());
        }
        let application = wide(python.as_os_str());
        let mut command = wide(OsStr::new(&format!(
            "\"{}\" -I -B -u \"{}\" --desktop-prepare",
            python.display(), bootstrap.display(),
        )));
        let directory = wide(root.as_os_str());
        unsafe {
            let job = CreateJobObjectW(None, PCWSTR::null()).map_err(|e| e.to_string())?;
            let job = OwnedHandle::from_raw_handle(job.0);
            let mut limits: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = zeroed();
            limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            SetInformationJobObject(
                handle(&job), JobObjectExtendedLimitInformation,
                &limits as *const _ as *const _, size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            ).map_err(|e| e.to_string())?;

            let mut read_pipe = HANDLE::default();
            let mut write_pipe = HANDLE::default();
            let attributes = SECURITY_ATTRIBUTES {
                nLength: size_of::<SECURITY_ATTRIBUTES>() as u32,
                lpSecurityDescriptor: ptr::null_mut(),
                bInheritHandle: BOOL(1),
            };
            CreatePipe(&mut read_pipe, &mut write_pipe, Some(&attributes), 0)
                .map_err(|e| e.to_string())?;
            let read_pipe = OwnedHandle::from_raw_handle(read_pipe.0);
            let write_pipe = OwnedHandle::from_raw_handle(write_pipe.0);
            SetHandleInformation(handle(&read_pipe), HANDLE_FLAG_INHERIT.0, HANDLE_FLAGS(0))
                .map_err(|e| e.to_string())?;

            let mut startup: STARTUPINFOW = zeroed();
            startup.cb = size_of::<STARTUPINFOW>() as u32;
            startup.dwFlags = STARTF_USESTDHANDLES;
            startup.hStdOutput = handle(&write_pipe);
            startup.hStdError = handle(&write_pipe);
            startup.hStdInput = HANDLE::default();
            let mut info: PROCESS_INFORMATION = zeroed();
            CreateProcessW(
                PCWSTR(application.as_ptr()), Some(PWSTR(command.as_mut_ptr())),
                None, None, true, CREATE_SUSPENDED | CREATE_NO_WINDOW,
                None, PCWSTR(directory.as_ptr()), &mut startup, &mut info,
            ).map_err(|e| format!("Could not start local preparation: {e}"))?;
            drop(write_pipe);
            let process = OwnedHandle::from_raw_handle(info.hProcess.0);
            let thread = OwnedHandle::from_raw_handle(info.hThread.0);
            if let Err(error) = AssignProcessToJobObject(handle(&job), handle(&process)) {
                let _ = TerminateProcess(handle(&process), 1);
                return Err(format!("Could not establish safe preparation ownership: {error}"));
            }
            if ResumeThread(handle(&thread)) == u32::MAX {
                let _ = TerminateJobObject(handle(&job), 1);
                return Err("Could not resume local preparation.".into());
            }
            Ok(Self { job, process, output: Mutex::new(File::from(read_pipe)) })
        }
    }

    pub fn run(&self, mut progress: impl FnMut(&str)) -> Result<(), String> {
        let mut output = self.output.lock().map_err(|_| "Preparation output is unavailable.")?;
        let mut buffer = [0u8; 4096];
        let mut line = Vec::new();
        let mut recent = String::new();
        loop {
            let count = output.read(&mut buffer)
                .map_err(|e| format!("Could not read preparation progress: {e}"))?;
            if count == 0 { break; }
            for &byte in &buffer[..count] {
                if byte == b'\n' || byte == b'\r' {
                    if !line.is_empty() {
                        let message = String::from_utf8_lossy(&line).trim().to_string();
                        if !message.is_empty() {
                            progress(&message);
                            recent.push_str(&message);
                            recent.push('\n');
                            if recent.len() > 6000 {
                                recent = recent.chars().rev().take(4000).collect::<String>().chars().rev().collect();
                            }
                        }
                        line.clear();
                    }
                } else if line.len() < 4096 {
                    line.push(byte);
                }
            }
        }
        if !line.is_empty() {
            let message = String::from_utf8_lossy(&line).trim().to_string();
            progress(&message);
            recent.push_str(&message);
        }
        let mut exit_code = 0;
        unsafe {
            if WaitForSingleObject(handle(&self.process), u32::MAX) != WAIT_OBJECT_0 {
                return Err("Could not confirm preparation process exit.".into());
            }
            GetExitCodeProcess(handle(&self.process), &mut exit_code).map_err(|e| e.to_string())?;
        }
        if exit_code != 0 {
            let reason = recent.lines().rev().find(|line| !line.trim().is_empty())
                .unwrap_or("Preparation stopped without a detailed error.");
            return Err(format!("Preparation failed (exit code {exit_code}): {reason}"));
        }
        Ok(())
    }

    pub fn terminate(&self) {
        unsafe { let _ = TerminateJobObject(handle(&self.job), 1); }
    }
}

pub fn listener_pid() -> Result<Option<u32>, String> {
    unsafe {
        let mut size = 0;
        let code = GetExtendedTcpTable(None, &mut size, false, AF_INET.0 as u32, TCP_TABLE_OWNER_PID_LISTENER, 0);
        if code != ERROR_INSUFFICIENT_BUFFER.0 && code != NO_ERROR.0 {
            return Err("Could not inspect the local port owner.".into());
        }
        // DWORD alignment for the variable-sized Windows table. Retry if it grew.
        for _ in 0..3 {
            let mut storage = vec![0u32; (size as usize + 3) / 4];
            let code = GetExtendedTcpTable(Some(storage.as_mut_ptr().cast()), &mut size, false, AF_INET.0 as u32, TCP_TABLE_OWNER_PID_LISTENER, 0);
            if code == ERROR_INSUFFICIENT_BUFFER.0 { continue; }
            if code != NO_ERROR.0 { return Err("Could not inspect the local port owner.".into()); }
            let table = storage.as_ptr().cast::<MIB_TCPTABLE_OWNER_PID>();
            let rows = std::slice::from_raw_parts(ptr::addr_of!((*table).table).cast::<windows::Win32::NetworkManagement::IpHelper::MIB_TCPROW_OWNER_PID>(), (*table).dwNumEntries as usize);
            let mut owner = None;
            for row in rows {
                if u16::from_be(row.dwLocalPort as u16) == 8000
                    && (row.dwLocalAddr == 0 || row.dwLocalAddr == u32::from_ne_bytes([127, 0, 0, 1]))
                {
                    if owner.is_some_and(|pid| pid != row.dwOwningPid) {
                        return Err("Port 8000 has ambiguous ownership. Close the conflicting service and retry.".into());
                    }
                    owner = Some(row.dwOwningPid);
                }
            }
            return Ok(owner);
        }
        Err("Port ownership changed during inspection. Retry startup.".into())
    }
}
