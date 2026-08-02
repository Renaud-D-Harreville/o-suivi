import { ref } from "vue";

const visible = ref(false);
const title = ref("");
const placeholder = ref("");
const defaultValue = ref("");

let resolvePromise: ((value: string | null) => void) | null = null;

export function usePrompt() {
  function prompt(
    promptTitle: string,
    options?: { placeholder?: string; defaultValue?: string },
  ): Promise<string | null> {
    title.value = promptTitle;
    placeholder.value = options?.placeholder || "";
    defaultValue.value = options?.defaultValue || "";
    visible.value = true;

    return new Promise<string | null>((resolve) => {
      resolvePromise = resolve;
    });
  }

  function handleConfirm(value: string): void {
    visible.value = false;
    resolvePromise?.(value);
    resolvePromise = null;
  }

  function handleCancel(): void {
    visible.value = false;
    resolvePromise?.(null);
    resolvePromise = null;
  }

  return {
    visible,
    title,
    placeholder,
    defaultValue,
    prompt,
    handleConfirm,
    handleCancel,
  };
}

