rule agent_skill_credential_exfiltration_webhook {
    meta:
        description = "Detects reading environment variables and sending to a webhook"
        severity = "HIGH"
    strings:
        $env1 = "os.environ"
        $env2 = "os.getenv"
        $post1 = "requests.post"
        $post2 = "urllib.request.urlopen"
    condition:
        ($env1 or $env2) and ($post1 or $post2)
}

rule agent_skill_remote_bootstrap_execution {
    meta:
        description = "Detects curl or wget piped to shell"
        severity = "CRITICAL"
    strings:
        $curl = "curl -s"
        $wget = "wget -qO-"
        $pipe_bash = "| bash"
        $pipe_sh = "| sh"
    condition:
        ($curl or $wget) and ($pipe_bash or $pipe_sh)
}

rule agent_skill_prompt_injection_hidden {
    meta:
        description = "Detects hidden prompt injection vectors"
        severity = "MEDIUM"
    strings:
        $zwsp = "\u200b"
        $html_comment = "<!-- system"
        $html_comment2 = "<!-- instruction"
    condition:
        $zwsp or $html_comment or $html_comment2
}

rule agent_skill_mcp_tool_poisoning {
    meta:
        description = "Detects homoglyphs or hidden metadata in tool definitions"
        severity = "HIGH"
    strings:
        $cyrillic_a = "а" 
        $cyrillic_e = "е"
    condition:
        $cyrillic_a or $cyrillic_e
}

rule agent_skill_cryptominer {
    meta:
        description = "Detects crypto mining artifacts"
        severity = "CRITICAL"
    strings:
        $xmrig = "xmrig" nocase
        $stratum = "stratum+tcp://"
        $pool = "pool."
    condition:
        $xmrig or $stratum or $pool
}

rule agent_skill_reverse_shell {
    meta:
        description = "Detects reverse shell patterns"
        severity = "CRITICAL"
    strings:
        $sock = "socket.socket"
        $pty = "pty.spawn"
        $sh = "/bin/sh"
        $bash = "/bin/bash"
    condition:
        $sock and $pty and ($sh or $bash)
}

rule agent_skill_data_staging {
    meta:
        description = "Detects data staging for exfiltration"
        severity = "HIGH"
    strings:
        $tar = "tar -czf"
        $zip = "zip -r"
        $ssh = ".ssh"
        $aws = ".aws"
    condition:
        ($tar or $zip) and ($ssh or $aws)
}

rule agent_skill_self_replication {
    meta:
        description = "Detects self-replication logic"
        severity = "HIGH"
    strings:
        $open_file = "open(__file__"
        $open_self = "open(\"__file__\""
        $write_skill1 = "open(\"SKILL.md\", \"w\")"
        $write_skill2 = "open('SKILL.md', 'w')"
        $shutil = "shutil.copy(__file__"
    condition:
        $open_file or $open_self or $write_skill1 or $write_skill2 or $shutil
}
