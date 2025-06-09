"use client"

import * as React from "react"

type ToastVariant = "default" | "destructive"

interface Toast {
  id: string
  title?: string
  description?: string
  variant?: ToastVariant
}

interface ToastState {
  toasts: Toast[]
}

let toastCount = 0

const listeners: Array<(state: ToastState) => void> = []
let memoryState: ToastState = { toasts: [] }

function dispatch(action: { type: string; toast?: Toast; toastId?: string }) {
  switch (action.type) {
    case "ADD_TOAST":
      if (action.toast) {
        memoryState = {
          toasts: [action.toast, ...memoryState.toasts].slice(0, 3),
        }
      }
      break
    case "REMOVE_TOAST":
      memoryState = {
        toasts: memoryState.toasts.filter((t) => t.id !== action.toastId),
      }
      break
  }

  listeners.forEach((listener) => {
    listener(memoryState)
  })
}

function toast({ title, description, variant = "default" }: Omit<Toast, "id">) {
  const id = (++toastCount).toString()

  dispatch({
    type: "ADD_TOAST",
    toast: { id, title, description, variant },
  })

  // Auto remove after 5 seconds
  setTimeout(() => {
    dispatch({ type: "REMOVE_TOAST", toastId: id })
  }, 5000)

  return { id }
}

export function useToast() {
  const [state, setState] = React.useState<ToastState>(memoryState)

  React.useEffect(() => {
    listeners.push(setState)
    return () => {
      const index = listeners.indexOf(setState)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }, [])

  return {
    toasts: state.toasts,
    toast,
  }
}
