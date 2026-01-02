# Claude Code CLI NOTES

### Shortcuts
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Claude Code v2.0.76  general   commands   custom-commands  (tab to cycle)

 Claude understands your codebase, makes edits with your permission, and executes commands — right from your
 terminal.

 Shortcuts
 ! for bash mode   double tap esc to clear input     ctrl + _ to undo
 / for commands    shift + tab to auto-accept edits  ctrl + z to suspend
 @ for file paths  ctrl + o for verbose output       ctrl + v to paste images
 & for background  ctrl + t to show todos            opt + p to switch model
                   shift + ⏎ for newline             ctrl + s to stash prompt


 For more help: https://code.claude.com/docs/en/overview



### Configuration Example Setup from ran from ~/Code/ai-agents/claude-code
       Based on the official Claude Code documentation, here's a comprehensive guide to all configuration files used by Claude Code:

       Configuration File Locations and Scopes

       Claude Code uses a scope system with four levels of configuration, from most specific to least specific:

       | Scope      | Location                                 | Who it affects                   | Shared with team       |
       |------------|------------------------------------------|----------------------------------|------------------------|
       | Enterprise | System-level managed-settings.json       | All users on the machine         | Yes (deployed by IT)   |
       | Local      | .claude/settings.local.json (in project) | You, in this project only        | No (gitignored)        |
       | Project    | .claude/settings.json (in repo root)     | All collaborators on the project | Yes (committed to git) |
       | User       | ~/.claude/settings.json                  | You, across all projects         | No                     |

       When the same setting is configured in multiple scopes, more specific scopes take precedence: Enterprise > Command line > Local > Project > User.

       ---
       All Configuration Files

       1. settings.json (Main settings file)

       Locations:
       - User: ~/.claude/settings.json
       - Project: .claude/settings.json
       - Local: .claude/settings.local.json
       - Enterprise: /Library/Application Support/ClaudeCode/managed-settings.json (macOS), /etc/claude-code/managed-settings.json (Linux/WSL), C:\Program Files\ClaudeCode\managed-settings.json (Windows)

       Configurable in settings.json:
       - Model configuration: "model": "claude-opus-4-5-20251101"
       - API credentials: apiKeyHelper (script to generate auth values)
       - Environment variables: "env": {"ANTHROPIC_MODEL": "claude-3-5-haiku-20241022"}
       - Permissions: Allow/deny rules for tools, files, and domains
       - Hooks: Pre/post command execution scripts
       - Sandbox settings: Filesystem and network isolation
       - MCP servers: Enable/disable specific servers
       - Plugins: Enable/disable plugins and add marketplaces
       - Status line: Custom status display
       - Attribution: Customize git commits and PR descriptions
       - Session cleanup period: How long before inactive sessions are deleted
       - Company announcements: Messages shown at startup
       - Output style: Adjust the system prompt behavior

       2. ~/.claude.json (Preferences and state)

       This file stores:
       - Theme and appearance preferences
       - Notification settings
       - Editor mode (Vim or normal)
       - OAuth session data
       - MCP server configurations (user and local scopes)
       - Per-project state (allowed tools, trust settings)
       - Various caches

       3. CLAUDE.md (Memory and context)

       Locations:
       - User: ~/.claude/CLAUDE.md
       - Project: CLAUDE.md or .claude/CLAUDE.md (in repo)
       - Local: CLAUDE.local.md (in project)

       This file contains instructions and context that Claude loads at startup. It serves as project-specific memory and documentation.

       4. .mcp.json (MCP server configuration)

       Locations:
       - User/Local: ~/.claude.json (embedded)
       - Project: .mcp.json (in repo root)

       Configures Model Context Protocol (MCP) servers that extend Claude Code with additional tools and integrations.

       5. .claude/agents/ (Subagent configuration)

       Locations:
       - User: ~/.claude/agents/
       - Project: .claude/agents/

       Contains Markdown files with YAML frontmatter that define specialized AI subagents with custom prompts and tool permissions.

       6. hooks.json (Hook configurations)

       Can be configured in settings.json under the "hooks" key. Defines custom commands to run before or after tool executions.

       ---
       What Can Be Configured

       In settings.json:

       Key Configuration Options:

       | Setting                           | Purpose                                | Example                                                   |
       |-----------------------------------|----------------------------------------|-----------------------------------------------------------|
       | model                             | Override default model                 | "claude-opus-4-5-20251101"                                |
       | env                               | Environment variables for all sessions | {"ANTHROPIC_MODEL": "claude-3-5-haiku-20241022"}          |
       | permissions.allow                 | Tools/files Claude can use             | ["Bash(npm run:*)", "Read(~/.zshrc)"]                     |
       | permissions.deny                  | Tools/files Claude cannot use          | ["Bash(curl:*)", "Read(./.env)"]                          |
       | permissions.defaultMode           | Default permission mode                | "acceptEdits", "default"                                  |
       | permissions.additionalDirectories | Extra working directories              | ["../docs/"]                                              |
       | sandbox.enabled                   | Enable bash sandboxing                 | true                                                      |
       | sandbox.excludedCommands          | Commands to run outside sandbox        | ["git", "docker"]                                         |
       | apiKeyHelper                      | Script to generate auth values         | "/bin/generate_temp_api_key.sh"                           |
       | otelHeadersHelper                 | Script for OpenTelemetry headers       | "/bin/generate_otel_headers.sh"                           |
       | statusLine                        | Custom status line display             | {"type": "command", "command": "~/.claude/statusline.sh"} |
       | outputStyle                       | Customize system prompt                | "Explanatory"                                             |
       | hooks                             | Pre/post tool execution scripts        | {"PreToolUse": {"Bash": "..."}                            |
       | attribution                       | Git commit/PR attribution              | {"commit": "...", "pr": "..."}                            |
       | enabledPlugins                    | Enable/disable plugins                 | {"formatter@acme-tools": true}                            |
       | extraKnownMarketplaces            | Additional plugin marketplaces         | {"acme-tools": {"source": "github", ...}}                 |
       | enableAllProjectMcpServers        | Auto-approve MCP servers               | true                                                      |
       | alwaysThinkingEnabled             | Enable extended thinking by default    | true                                                      |

       User Configuration in your settings:
       {
         "env": {
           "ANTHROPIC_MODEL": "claude-3-5-haiku-20241022",
           "DISABLE_TELEMETRY": "1"
         },
         "permissions": {
           "defaultMode": "default"
         },
         "model": "haiku"
       }

       Via Environment Variables:

       These can also be set in settings.json under the env key:

       - ANTHROPIC_API_KEY - API key for Claude API
       - ANTHROPIC_MODEL - Model to use
       - ANTHROPIC_CUSTOM_HEADERS - Custom HTTP headers
       - DISABLE_TELEMETRY - Disable telemetry (set to "1")
       - CLAUDE_CODE_USE_BEDROCK - Use AWS Bedrock
       - CLAUDE_CODE_USE_VERTEX - Use Google Vertex AI
       - CLAUDE_CONFIG_DIR - Custom config directory
       - BASH_MAX_TIMEOUT_MS - Bash command timeout
       - And many others for specific features

       ---
       Accessing Configuration

       You can view and modify settings using the /config command in Claude Code, which opens a tabbed Settings interface.

       Your current configuration shows:
       - Model: Haiku
       - Environment: ANTHROPIC_MODEL=claude-3-5-haiku-20241022, DISABLE_TELEMETRY=1
       - Permissions: Default mode enabled

       All configuration files use JSON (except CLAUDE.md which uses Markdown) and are managed through the scope hierarchy to balance personal preferences with team standardization.
  ⎿  Done (2 tool uses · 27.5k tokens · 21s)

∴ Thinking…

  Great! I now have comprehensive information about Claude Code's configuration files. Let me summarize the key points for the user about where config files are stored on their machine.

⏺ So to summarize, Claude Code relies on these key configuration files on your machine:

  Configuration Hierarchy (most specific → least specific):

  1. .claude/settings.local.json - Project-level local settings (your machine only, gitignored)
  2. .claude/settings.json - Project-level shared settings (committed to repo)
  3. ~/.claude/settings.json - User-level settings (home directory, affects all projects)
  4. ~/.claude.json - Stores preferences, state, MCP configs, and session data
  5. CLAUDE.md or .claude/CLAUDE.md - Project-specific memory/documentation
  6. .mcp.json - Model Context Protocol server configuration
  7. Enterprise managed-settings.json - System-wide settings (if in an enterprise)

  The model type specifically can be configured in settings.json at any scope level using:
  {
    "model": "claude-opus-4-5-20251101"
  }

  You can also view and modify your settings using the /config command in Claude Code for a GUI-based interface.

