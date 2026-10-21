import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merges conditional class names (clsx) then dedupes conflicting Tailwind
 * utility classes (tailwind-merge). Every shadcn/ui component uses this. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
