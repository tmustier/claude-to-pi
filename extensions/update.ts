import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { execSync } from "child_process";

export default function (pi: ExtensionAPI) {
  pi.registerCommand("update", {
    description: "Update pi to the latest version and reload",
    handler: async (_args, ctx) => {
      ctx.ui.notify("Updating pi...", "info");

      try {
        const output = execSync(
          "npm install -g @mariozechner/pi-coding-agent 2>&1 && pi update 2>&1",
          { encoding: "utf-8", timeout: 120_000 }
        );
        ctx.ui.notify("Pi updated. Reloading...", "success");
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        ctx.ui.notify(`Update failed: ${message}`, "error");
        return;
      }

      await ctx.reload();
      return;
    },
  });
}
