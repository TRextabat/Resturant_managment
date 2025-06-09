"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, Minus } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiClient } from "@/lib/api"
import type { MenuItem, MenuCategory, Table, CreateOrderRequest } from "@/lib/types"

interface CartItem extends MenuItem {
  quantity: number
}

export default function CustomerMenu() {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [categories, setCategories] = useState<MenuCategory[]>([])
  const [tables, setTables] = useState<Table[]>([])
  const [allTables, setAllTables] = useState<Table[]>([]) // Store all tables for lookup
  const [cart, setCart] = useState<CartItem[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>("All")
  const [selectedTable, setSelectedTable] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [userOrders, setUserOrders] = useState<any[]>([])
  const [showOrders, setShowOrders] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadData()
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const userResponse = await apiClient.getCurrentUser()
    if (userResponse.data && !userResponse.error) {
      setCurrentUser(userResponse.data)
      loadUserOrders()
    }
  }

  const loadUserOrders = async () => {
    const response = await apiClient.getMyOrders()
    if (response.data) {
      setUserOrders(response.data)
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const [itemsResponse, categoriesResponse, tablesResponse] = await Promise.all([
        apiClient.getMenuItems(),
        apiClient.getMenuCategories(),
        apiClient.getTables(),
      ])

      if (itemsResponse.data) {
        setMenuItems(itemsResponse.data)
      }
      if (categoriesResponse.data) {
        setCategories(categoriesResponse.data)
      }
      if (tablesResponse.data) {
        setAllTables(tablesResponse.data) // Store all tables for lookup
        setTables(tablesResponse.data.filter((table) => !table.is_occupied))
      }
    } catch (error) {
      toast({
        title: "Error loading data",
        description: "Failed to load menu and table information",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const getTableName = (tableId: string) => {
    const table = allTables.find((t) => t.id === tableId)
    return table ? `Table ${table.table_number}` : `Table ${tableId.slice(0, 8)}`
  }

  const filteredItems =
      selectedCategory === "All"
          ? menuItems
          : menuItems.filter((item) => {
            const category = categories.find((cat) => cat.id === item.category_id)
            return category?.name === selectedCategory
          })

  const addToCart = (item: MenuItem) => {
    setCart((prev) => {
      const existing = prev.find((cartItem) => cartItem.id === item.id)
      if (existing) {
        return prev.map((cartItem) =>
            cartItem.id === item.id ? { ...cartItem, quantity: cartItem.quantity + 1 } : cartItem,
        )
      }
      return [...prev, { ...item, quantity: 1 }]
    })
  }

  const removeFromCart = (itemId: string) => {
    setCart((prev) => {
      const existing = prev.find((cartItem) => cartItem.id === itemId)
      if (existing && existing.quantity > 1) {
        return prev.map((cartItem) =>
            cartItem.id === itemId ? { ...cartItem, quantity: cartItem.quantity - 1 } : cartItem,
        )
      }
      return prev.filter((cartItem) => cartItem.id !== itemId)
    })
  }

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + Number.parseFloat(item.price) * item.quantity, 0)
  }

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0)
  }

  const handleLogout = async () => {
    await apiClient.logout()
    setCurrentUser(null)
    setUserOrders([])
    toast({
      title: "Logged out",
      description: "You have been logged out successfully",
    })
  }

  const placeOrder = async () => {
    if (cart.length === 0) {
      toast({
        title: "Cart is empty",
        description: "Please add items to your cart before placing an order.",
        variant: "destructive",
      })
      return
    }

    if (!selectedTable) {
      toast({
        title: "Table not selected",
        description: "Please select a table before placing an order.",
        variant: "destructive",
      })
      return
    }

    const orderData: CreateOrderRequest = {
      table_id: selectedTable,
      items: cart.map((item) => ({
        menu_item_id: item.id,
        item_name: item.name,
        unit_price: Number.parseFloat(item.price),
        quantity: item.quantity,
      })),
    }

    const response = await apiClient.createOrder(orderData)

    if (response.error) {
      // If unauthorized, suggest login but allow guest orders
      if (response.error.includes("401") || response.error.includes("unauthorized")) {
        toast({
          title: "Login recommended",
          description: "Login to track your order status, or continue as guest.",
          variant: "default",
        })
      } else {
        toast({
          title: "Order failed",
          description: response.error,
          variant: "destructive",
        })
      }
    } else {
      toast({
        title: "Order placed successfully!",
        description: `Your order for $${getTotalPrice().toFixed(2)} has been sent to the kitchen.`,
      })
      setCart([])
      setSelectedTable("")
      loadData()
      // Refresh user orders if logged in
      if (currentUser) {
        loadUserOrders()
      }
    }
  }

  const categoryNames = ["All", ...categories.map((cat) => cat.name)]

  if (loading) {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading menu...</p>
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
                <h1 className="text-3xl font-bold">Bella Vista Restaurant</h1>
                <p className="text-muted-foreground">Authentic Italian Cuisine</p>
              </div>
              <div className="flex items-center gap-4">
                {currentUser ? (
                    <>
                      <span className="text-sm text-muted-foreground">Welcome, {currentUser.primary_email}</span>
                      <Button variant="outline" onClick={() => setShowOrders(!showOrders)}>
                        My Orders ({userOrders.length})
                      </Button>
                      <Button variant="outline" onClick={handleLogout}>
                        Logout
                      </Button>
                    </>
                ) : (
                    <>
                      <Button variant="outline" asChild>
                        <a href="/login">Login</a>
                      </Button>
                    </>
                )}
                <Button variant="outline" asChild>
                  <a href="/staff-login">Staff Login</a>
                </Button>
              </div>
            </div>
          </div>
        </header>

        {showOrders && currentUser && (
            <div className="border-b bg-muted/50">
              <div className="container mx-auto px-4 py-6">
                <h2 className="text-xl font-semibold mb-4">My Orders</h2>
                {userOrders.length === 0 ? (
                    <p className="text-muted-foreground">No orders yet</p>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {userOrders.map((order) => (
                          <Card key={order.id}>
                            <CardHeader>
                              <div className="flex justify-between items-start">
                                <div>
                                  <CardTitle className="text-sm">Order #{order.id.slice(0, 8)}</CardTitle>
                                  <CardDescription>{getTableName(order.table_id)}</CardDescription>
                                </div>
                                <Badge
                                    variant={
                                      order.status === "ready"
                                          ? "default"
                                          : order.status === "served"
                                              ? "secondary"
                                              : order.status === "canceled"
                                                  ? "destructive"
                                                  : "outline"
                                    }
                                >
                                  {order.status}
                                </Badge>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-1 text-sm">
                                {order.items.map((item: any) => (
                                    <div key={item.menu_item_id} className="flex justify-between">
                            <span>
                              {item.quantity}x {item.item_name}
                            </span>
                                      <span>${item.line_total}</span>
                                    </div>
                                ))}
                                <div className="border-t pt-1 font-semibold">
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
        )}

        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-3">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold mb-4">Our Menu</h2>
                <div className="flex flex-wrap gap-2">
                  {categoryNames.map((category) => (
                      <Button
                          key={category}
                          variant={selectedCategory === category ? "default" : "outline"}
                          onClick={() => setSelectedCategory(category)}
                      >
                        {category}
                      </Button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredItems.map((item) => {
                  const category = categories.find((cat) => cat.id === item.category_id)
                  return (
                      <Card key={item.id} className="overflow-hidden">
                        <div className="aspect-video relative bg-muted">
                          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                            No Image
                          </div>
                        </div>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div>
                              <CardTitle className="text-lg">{item.name}</CardTitle>
                              <CardDescription className="text-sm mt-1">{item.description}</CardDescription>
                            </div>
                            <Badge variant="secondary">{category?.name || "Unknown"}</Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="flex justify-between items-center">
                            <span className="text-2xl font-bold">${Number.parseFloat(item.price).toFixed(2)}</span>
                            <Button onClick={() => addToCart(item)}>
                              <Plus className="h-4 w-4 mr-2" />
                              Add to Cart
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                  )
                })}
              </div>
            </div>

            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle>Your Order</CardTitle>
                  {getTotalItems() > 0 && (
                      <Badge variant="secondary" className="w-fit">
                        {getTotalItems()} {getTotalItems() === 1 ? "item" : "items"}
                      </Badge>
                  )}
                </CardHeader>
                <CardContent>
                  {/* Table Selection */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">Select Table</label>
                    <select
                        value={selectedTable}
                        onChange={(e) => setSelectedTable(e.target.value)}
                        className="w-full p-2 border rounded-md"
                    >
                      <option value="">Choose a table</option>
                      {tables.map((table) => (
                          <option key={table.id} value={table.id}>
                            Table {table.table_number} (Capacity: {table.capacity})
                          </option>
                      ))}
                    </select>
                  </div>

                  {cart.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">Your cart is empty</p>
                  ) : (
                      <div className="space-y-4">
                        {cart.map((item) => (
                            <div key={item.id} className="flex justify-between items-center">
                              <div className="flex-1">
                                <h4 className="font-medium">{item.name}</h4>
                                <p className="text-sm text-muted-foreground">
                                  ${Number.parseFloat(item.price).toFixed(2)} × {item.quantity}
                                </p>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button size="icon" variant="outline" onClick={() => removeFromCart(item.id)}>
                                  <Minus className="h-3 w-3" />
                                </Button>
                                <span className="w-8 text-center">{item.quantity}</span>
                                <Button size="icon" variant="outline" onClick={() => addToCart(item)}>
                                  <Plus className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                        ))}
                        <div className="border-t pt-4">
                          <div className="flex justify-between items-center font-semibold text-lg">
                            <span>Total:</span>
                            <span>${getTotalPrice().toFixed(2)}</span>
                          </div>
                          <Button
                              className="w-full mt-4"
                              onClick={placeOrder}
                              disabled={!selectedTable || cart.length === 0}
                          >
                            Place Order
                          </Button>
                        </div>
                      </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
  )
}
