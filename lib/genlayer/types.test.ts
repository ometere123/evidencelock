import { describe, expect, it } from "vitest";
import { claimSchema } from "./types";

describe("claim schema", () => {
  it("rejects incomplete chain data", () => {
    expect(claimSchema.safeParse({ claim_id: "C-1" }).success).toBe(false);
  });
});
