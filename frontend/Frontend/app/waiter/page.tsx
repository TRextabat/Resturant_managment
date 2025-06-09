"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle, XCircle, Clock, User, LogOut } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiClient } from "@/lib/api"
import type { Order, Table } from "@/lib/types"

export default function WaiterDashboard() {
  const [orders, setOrders] = useState<Order[]>([])
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [hasNewOrders, setHasNewOrders] = useState(false)
  const [lastOrderCount, setLastOrderCount] = useState(0)
  const [activeTab, setActiveTab] = useState("new")
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    checkAuth()
  }, [router])

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

    // Check if user has waiter role (adjust based on your backend)
    if (user.role && user.role !== "waiter" && user.role !== "admin") {
      toast({
        title: "Access denied",
        description: "This dashboard is for waiters only",
        variant: "destructive",
      })
      router.push("/staff-login")
      return
    }

    setCurrentUser(user)
    loadTables()
  }

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

  const loadOrders = async () => {
    setLoading(true)
    try {
      if (!currentUser) return

      // Use getOrdersForWaiter with the current user's ID
      const response = await apiClient.getOrdersForWaiter(currentUser.id)

      if (response.data) {
        const newOrders = response.data.filter((order: Order) => order.status === "new")

        // Check if there are new orders since last check
        if (newOrders.length > lastOrderCount && lastOrderCount > 0) {
          setHasNewOrders(true)
        }

        setOrders(response.data)
        setLastOrderCount(newOrders.length)
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

  const handleTabChange = (value: string) => {
    setActiveTab(value)
    // Clear notification when user clicks on new orders tab
    if (value === "new") {
      setHasNewOrders(false)
    }
  }

  const handleApproveOrder = async (orderId: string) => {
    if (!currentUser) return

    const response = await apiClient.approveOrderByWaiter(orderId, currentUser.id)

    if (response.error) {
      toast({
        title: "Error",
        description: response.error,
        variant: "destructive",
      })
    } else {
      toast({
        title: "Order approved",
        description: "Order has been sent to the kitchen",
      })
      loadOrders()
    }
  }

  const handleUpdateOrderStatus = async (orderId: string, newStatus: string) => {
    const response = await apiClient.updateOrderStatus(orderId, newStatus)

    if (response.error) {
      toast({
        title: "Error",
        description: response.error,
        variant: "destructive",
      })
    } else {
      toast({
        title: "Order updated",
        description: `Order status changed to ${newStatus}`,
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
              <CheckCircle className="w-3 h-3 mr-1" />
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
              <User className="w-3 h-3 mr-1" />
              Served
            </Badge>
        )
      case "canceled":
        return (
            <Badge variant="destructive">
              <XCircle className="w-3 h-3 mr-1" />
              Canceled
            </Badge>
        )
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const newOrders = orders.filter((order) => order.status === "new")
  const readyOrders = orders.filter((order) => order.status === "ready")
  const servedOrders = orders.filter((order) => order.status === "served")
  const canceledOrders = orders.filter((order) => order.status === "canceled")

  useEffect(() => {
    if (currentUser) {
      loadOrders()

      // Set up polling that only updates the data without resetting UI state
      const interval = setInterval(() => {
        // Use a silent version of loadOrders that doesn't trigger loading state
        const silentLoadOrders = async () => {
          try {
            if (!currentUser) return

            const response = await apiClient.getOrdersForWaiter(currentUser.id)
            if (response.data) {
              const newOrdersCount = response.data.filter((order: Order) => order.status === "new").length

              // Check if there are new orders since last check
              if (newOrdersCount > lastOrderCount && lastOrderCount > 0) {
                setHasNewOrders(true)
              }

              setOrders(response.data)
              setLastOrderCount(newOrdersCount)
            }
          } catch (error) {
            console.error("Error refreshing orders:", error)
          }
        }

        silentLoadOrders()
      }, 10000) // Increased to 10 seconds to reduce unnecessary refreshes

      return () => clearInterval(interval)
    }
  }, [currentUser, lastOrderCount])

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
                <h1 className="text-2xl font-bold">Waiter Dashboard</h1>
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
          <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="new" className="relative">
                New Orders ({newOrders.length})
                {hasNewOrders && activeTab !== "new" && (
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                )}
              </TabsTrigger>
              <TabsTrigger value="ready">Ready Orders ({readyOrders.length})</TabsTrigger>
              <TabsTrigger value="served">Served ({servedOrders.length})</TabsTrigger>
              <TabsTrigger value="canceled">Canceled ({canceledOrders.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="new" className="space-y-4">
              <div className="grid gap-4">
                {newOrders.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <p className="text-muted-foreground">No new orders</p>
                      </CardContent>
                    </Card>
                ) : (
                    newOrders.map((order) => (
                        <Card key={order.id}>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-lg">Order #{order.id.slice(0, 8)}</CardTitle>
                                <CardDescription>{getTableName(order.table_id)}</CardDescription>
                              </div>
                              {getStatusBadge(order.status)}
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2 mb-4">
                              {order.items.map((item) => (
                                  <div key={item.menu_item_id} className="flex justify-between">
                            <span>
                              {item.quantity}x {item.item_name}
                            </span>
                                    <span>${item.line_total}</span>
                                  </div>
                              ))}
                              {order.special_request && (
                                  <div className="text-sm text-muted-foreground">Special request: {order.special_request}</div>
                              )}
                              <div className="border-t pt-2 font-semibold">
                                <div className="flex justify-between">
                                  <span>Total:</span>
                                  <span>${order.total_amount}</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button onClick={() => handleUpdateOrderStatus(order.id, "in_progress")} className="flex-1">
                                <CheckCircle className="w-4 h-4 mr-2" />
                                Approve Order
                              </Button>
                              <Button
                                  variant="destructive"
                                  onClick={() => handleUpdateOrderStatus(order.id, "canceled")}
                                  className="flex-1"
                              >
                                <XCircle className="w-4 h-4 mr-2" />
                                Cancel Order
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                    ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="ready" className="space-y-4">
              <div className="grid gap-4">
                {readyOrders.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <p className="text-muted-foreground">No ready orders</p>
                      </CardContent>
                    </Card>
                ) : (
                    readyOrders.map((order) => (
                        <Card key={order.id}>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-lg">Order #{order.id.slice(0, 8)}</CardTitle>
                                <CardDescription>Ready for pickup - {getTableName(order.table_id)}</CardDescription>
                              </div>
                              {getStatusBadge(order.status)}
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2 mb-4">
                              {order.items.map((item) => (
                                  <div key={item.menu_item_id} className="flex justify-between">
                            <span>
                              {item.quantity}x {item.item_name}
                            </span>
                                    <span>${item.line_total}</span>
                                  </div>
                              ))}
                              <div className="border-t pt-2 font-semibold">
                                <div className="flex justify-between">
                                  <span>Total:</span>
                                  <span>${order.total_amount}</span>
                                </div>
                              </div>
                            </div>
                            <Button onClick={() => handleUpdateOrderStatus(order.id, "served")} className="w-full">
                              <User className="w-4 h-4 mr-2" />
                              Mark as Served
                            </Button>
                          </CardContent>
                        </Card>
                    ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="served" className="space-y-4">
              <div className="grid gap-4">
                {servedOrders.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <p className="text-muted-foreground">No served orders</p>
                      </CardContent>
                    </Card>
                ) : (
                    servedOrders.map((order) => (
                        <Card key={order.id}>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-lg">Order #{order.id.slice(0, 8)}</CardTitle>
                                <CardDescription>Completed order - {getTableName(order.table_id)}</CardDescription>
                              </div>
                              {getStatusBadge(order.status)}
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {order.items.map((item) => (
                                  <div key={item.menu_item_id} className="flex justify-between">
                            <span>
                              {item.quantity}x {item.item_name}
                            </span>
                                    <span>${item.line_total}</span>
                                  </div>
                              ))}
                              <div className="border-t pt-2 font-semibold">
                                <div className="flex justify-between">
                                  <span>Total:</span>
                                  <span>${order.total_amount}</span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                    ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="canceled" className="space-y-4">
              <div className="grid gap-4">
                {canceledOrders.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <p className="text-muted-foreground">No canceled orders</p>
                      </CardContent>
                    </Card>
                ) : (
                    canceledOrders.map((order) => (
                        <Card key={order.id}>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-lg">Order #{order.id.slice(0, 8)}</CardTitle>
                                <CardDescription>Canceled order - {getTableName(order.table_id)}</CardDescription>
                              </div>
                              {getStatusBadge(order.status)}
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {order.items.map((item) => (
                                  <div key={item.menu_item_id} className="flex justify-between">
                            <span>
                              {item.quantity}x {item.item_name}
                            </span>
                                    <span>${item.line_total}</span>
                                  </div>
                              ))}
                              <div className="border-t pt-2 font-semibold">
                                <div className="flex justify-between">
                                  <span>Total:</span>
                                  <span>${order.total_amount}</span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                    ))
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
  )
}
