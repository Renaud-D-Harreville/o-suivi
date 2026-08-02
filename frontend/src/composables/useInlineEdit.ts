import { ref } from "vue";

export function useInlineEdit() {
  const editingField = ref<{ userId: string; field: string } | null>(null);
  const editValue = ref("");

  function startEdit(userId: string, field: string, currentValue: string | number | null): void {
    editingField.value = { userId, field };
    editValue.value = currentValue?.toString() || "";
  }

  function cancelEdit(): void {
    editingField.value = null;
    editValue.value = "";
  }

  function isEditing(userId: string, field: string): boolean {
    return editingField.value?.userId === userId && editingField.value?.field === field;
  }

  function clearEdit(): void {
    editingField.value = null;
    editValue.value = "";
  }

  return { editingField, editValue, startEdit, cancelEdit, isEditing, clearEdit };
}

