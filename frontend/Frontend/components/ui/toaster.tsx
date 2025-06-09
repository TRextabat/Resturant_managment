"use client"

import { useToast } from "@/hooks/use-toast"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            max-w-sm p-4 rounded-lg shadow-lg border animate-in slide-in-from-top-2
            ${
              toast.variant === "destructive"
                ? "bg-red-50 border-red-200 text-red-900"
                : "bg-white border-gray-200 text-gray-900"
            }
          `}
        >
          {toast.title && <div className="font-semibold text-sm mb-1">{toast.title}</div>}
          {toast.description && <div className="text-sm opacity-90">{toast.description}</div>}
        </div>
      ))}
    </div>
  )
}
