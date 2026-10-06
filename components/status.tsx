export function Chip({ value }: { value: string }) { return <span className={`chip ${value.toLowerCase().replaceAll("_", "-")}`}>{value || "PENDING"}</span>; }
export function Hash({ value }: { value: string }) { return <code title={value}>{value ? `${value.slice(0, 10)}…${value.slice(-8)}` : "—"}</code>; }
