# Permissioned integration boundaries

`marketplace.connectors.preflight` is a metadata-only policy check. The trusted host must authenticate the principal, verify the authorization grant and obtain trustworthy channel metadata before calling it. An administrator reference string is not proof of written authorization. No MCP or Discord transport is implemented.

Slack's official MCP endpoint is https://mcp.slack.com/mcp using Streamable HTTP. It requires a registered fixed app identity; Slack currently allows internal or Marketplace-published apps, not unlisted apps. OAuth scopes, user consent and workspace app approval remain separate obligations. Request only the public read scopes required for the selected tool. Do not permit generic tool execution or expose send tools. Unknown/private/DM/shared channel metadata fails closed.

[Slack documentation](https://docs.slack.dev/ai/slack-mcp-server/) checked 2026-09-07.

For Discord, use an authorized bot application and official API. No claim of an official Discord MCP server is made. A future MCP wrapper must retain the same permissions and audit boundaries. Red (GPL-3.0) and YAGPDB (MIT) are candidates for separate evaluation, not bundled dependencies. Assess licenses, dependencies and permissions before integration.

[Discord privileged intent review](https://support-dev.discord.com/hc/en-us/articles/40281523410967-Changes-to-Privileged-Intent-Access-for-Discord-Apps) is distinct from administrator consent and marketplace verification.
