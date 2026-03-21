import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerShortcut("ctrl+shift+enter", {
    description: "Send 'continue' to the agent",
    handler: async (ctx) => {
      pi.sendUserMessage("continue");
    },
  });
}
