export function copyToClipboard(text: string): void {
  try {
    navigator.clipboard.writeText(text);
  } catch {
    // Fallback for older browsers / insecure context
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
}

export function copyPhone(phone: string): void {
  copyToClipboard(phone);
}

