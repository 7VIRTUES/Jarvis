use std::{
    ffi::OsStr,
    mem::{size_of, zeroed},
    os::windows::{ffi::OsStrExt, io::{AsRawHandle, FromRawHandle, OwnedHandle}},
    path::Path,
    ptr,
};
use windows::{
    core::{PCWSTR, PWSTR},
    Win32::{
        Foundation::{HANDLE, ERROR_INSUFFICIENT_BUFFER, NO_ERROR, WAIT_TIMEOUT},
        NetworkManagement::IpHelper::{GetExtendedTcpTable, MIB_TCPTABLE_OWNER_PID, TCP_TABLE_OWNER_PID_LISTENER},
        Networking::WinSock::AF_INET,
        System::{
            JobObjects::{AssignProcessToJobObject, CreateJobObjectW, IsProcessInJob,
                JobObjectExtendedLimitInformation, SetInformationJobObject,
                JOBOBJECT_EXTENDED_LIMIT_INFORMATION, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE},
            Threading::{CreateProcessW, OpenProcess, ResumeThread, TerminateProcess,
                WaitForSingleObject, CREATE_NO_WINDOW, CREATE_SUSPENDED,
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
