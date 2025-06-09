"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Clock, ChefHat, LogOut } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiClient } from "@/lib/api"
import type { Order, Table } from "@/lib/types"

export default function KitchenDashboard() {
  const [orders, setOrders] = useState<Order[]>([])
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const router = useRouter()
  const { toast } = useToast()

  const checkAuth = async () => {
    const userResponse = await apiClient.getCurrentUser()

    if (userResponse.error) {
      toast({
        title: "Authentication required",
        description: "Please login with your staff credentials",
        variant: "destructive",
      })
      router.push("/staff-login")
      return
    }

    const user = userResponse.data

    // Check if user has kitchen role (adjust based on your backend)
    if (user.role && user.role !== "kitchen" && user.role !== "admin") {
      toast({
        title: "Access denied",
        description: "This dashboard is for kitchen staff only",
        variant: "destructive",
      })
      router.push("/staff-login")
      return
    }

    setCurrentUser(user)
    loadTables()
    loadOrders()
  }

  useEffect(() => {
    checkAuth()
  }, [router])

  const loadTables = async () => {
    try {
      const response = await apiClient.getTables()
      if (response.data) {
        setTables(response.data)
      }
    } catch (error) {
      console.error("Error loading tables:", error)
    }
  }

  const getTableName = (tableId: string) => {
    const table = tables.find((t) => t.id === tableId)
    return table ? `Table ${table.table_number}` : `Table ${tableId.slice(0, 8)}`
  }

  useEffect(() => {
    if (!currentUser) return

    // Set up polling that only updates the data without resetting UI state
    const interval = setInterval(() => {
      // Use a silent version of loadOrders that doesn't trigger loading state
      const silentLoadOrders = async () => {
        try {
          const response = await apiClient.getOrdersForKitchen()
          if (response.data) {
            setOrders(response.data)
          }
        } catch (error) {
          console.error("Error refreshing orders:", error)
        }
      }

      silentLoadOrders()
    }, 10000) // Increased to 10 seconds to reduce unnecessary refreshes

    return () => clearInterval(interval)
  }, [currentUser])

  const loadOrders = async () => {
    try {
      const response = await apiClient.getOrdersForKitchen()

      if (response.data) {
        setOrders(response.data)
      } else if (response.error) {
        toast({
          title: "Error loading orders",
          description: response.error,
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load orders",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleMarkReady = async (orderId: string) => {
    const response = await apiClient.updateOrderStatus(orderId, "ready")

    if (response.error) {
      toast({
        title: "Error",
        description: response.error,
        variant: "destructive",
      })
    } else {
      toast({
        title: "Order ready",
        description: "Order has been marked as ready for pickup",
      })
      loadOrders()
    }
  }

  const handleLogout = async () => {
    await apiClient.logout()
    router.push("/")
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "new":
        return (
            <Badge variant="secondary">
              <Clock className="w-3 h-3 mr-1" />
              New
            </Badge>
        )
      case "in_progress":
        return (
            <Badge variant="default">
              <ChefHat className="w-3 h-3 mr-1" />
              In Progress
            </Badge>
        )
      case "ready":
        return (
            <Badge variant="outline" className="border-green-500 text-green-600">
              Ready
            </Badge>
        )
      case "served":
        return (
            <Badge variant="default" className="bg-green-600">
              Served
            </Badge>
        )
      case "canceled":
        return <Badge variant="destructive">Canceled</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "new":
        return "border-l-yellow-500"
      case "in_progress":
        return "border-l-blue-500"
      case "ready":
        return "border-l-green-500"
      case "served":
        return "border-l-gray-500"
      case "canceled":
        return "border-l-red-500"
      default:
        return "border-l-gray-300"
    }
  }

  const newOrders = orders.filter((order) => order.status === "new")
  const inProgressOrders = orders.filter((order) => order.status === "in_progress")
  const readyOrders = orders.filter((order) => order.status === "ready")
  const servedOrders = orders.filter((order) => order.status === "served")
  const canceledOrders = orders.filter((order) => order.status === "canceled")

  if (loading) {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading orders...</p>
          </div>
        </div>
    )
  }

  return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold">Kitchen Dashboard</h1>
                <p className="text-muted-foreground">Welcome, {currentUser?.primary_email}</p>
              </div>
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">New Orders</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{newOrders.length}</div>
                <p className="text-xs text-muted-foreground">Waiting for approval</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{inProgressOrders.length}</div>
                <p className="text-xs text-muted-foreground">Currently cooking</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Ready</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{readyOrders.length}</div>
                <p className="text-xs text-muted-foreground">Ready for pickup</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Served</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{servedOrders.length}</div>
                <p className="text-xs text-muted-foreground">Completed orders</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Canceled</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{canceledOrders.length}</div>
                <p className="text-xs text-muted-foreground">Canceled orders</p>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <h2 className="text-xl font-semibold">All Orders</h2>

            {orders.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <p className="text-muted-foreground">No orders yet</p>
                  </CardContent>
                </Card>
            ) : (
                <div className="grid gap-4">
                  {orders
                      .sort((a, b) => new Date(b.id).getTime() - new Date(a.id).getTime())
                      .map((order) => (
                          <Card key={order.id} className={`border-l-4 ${getStatusColor(order.status)}`}>
                            <CardHeader>
                              <div className="flex justify-between items-start">
                                <div>
                                  <CardTitle className="text-lg">Order #{order.id.slice(0, 8)}</CardTitle>
                                  <CardDescription>{getTableName(order.table_id)}</CardDescription>
                                </div>
                                <div className="flex items-center gap-2">
                                  {getStatusBadge(order.status)}
                                  {order.status === "in_progress" && (
                                      <Button size="sm" onClick={() => handleMarkReady(order.id)}>
                                        <CheckCircle className="w-4 h-4 mr-2" />
                                        Mark Ready
                                      </Button>
                                  )}
                                </div>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-2">
                                {order.items.map((item) => (
                                    <div key={item.menu_item_id} className="flex justify-between">
                            <span className="font-medium">
                              {item.quantity}x {item.item_name}
                            </span>
                                      <span>${item.line_total}</span>
                                    </div>
                                ))}
                                {order.special_request && (
                                    <div className="text-sm text-muted-foreground bg-muted p-2 rounded">
                                      <strong>Special request:</strong> {order.special_request}
                                    </div>
                                )}
                                <div className="border-t pt-2 font-semibold">
                                  <div className="flex justify-between">
                                    <span>Total:</span>
                                    <span>${order.total_amount}</span>
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                      ))}
                </div>
            )}
          </div>
        </div>
      </div>
  )
}
