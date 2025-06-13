"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Eye, EyeOff } from "lucide-react"
import { apiClient } from "@/lib/api"
import { Separator } from "@/components/ui/separator"

export default function StaffLoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [expectedRole, setExpectedRole] = useState<"waiter" | "kitchen">("waiter")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await apiClient.login(email, password)

      if (response.error) {
        toast({
          title: "Login failed",
          description: response.error,
          variant: "destructive",
        })
      } else {
        // Get user profile to check role
        const userResponse = await apiClient.getCurrentUser()

        if (userResponse.data) {
          // For now, we'll assume the backend returns role information
          // You may need to adjust this based on your actual backend response
          const userRole = userResponse.data.role || expectedRole // Fallback to expected role

          // Verify the user has the expected staff role
          if (userRole === "customer") {
            toast({
              title: "Access denied",
              description: "This login is for staff only. Please use the customer login.",
              variant: "destructive",
            })
            await apiClient.logout()
            return
          }

          toast({
            title: "Login successful",
            description: `Welcome back, ${userRole === "kitchen" ? "Kitchen Staff" : "Waiter"}!`,
          })

          // Redirect based on role
          if (userRole === "kitchen") {
            router.push("/kitchen")
          } else if (userRole === "waiter") {
            router.push("/waiter")
          } else {
            // Default to kitchen for now
            router.push("/kitchen")
          }
        }
      }
    } catch (error) {
      toast({
        title: "Login failed",
        description: "An unexpected error occurred",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleLogin = () => {
    toast({
      title: "Feature not ready",
      description: "Google login is coming soon!",
      variant: "default",
    })
  }

  return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Staff Login</CardTitle>
            <CardDescription>Sign in to access your staff dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="role">Expected Role</Label>
                <Select value={expectedRole} onValueChange={(value: "waiter" | "kitchen") => setExpectedRole(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="waiter">Waiter</SelectItem>
                    <SelectItem value="kitchen">Kitchen Staff</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your work email"
                    required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      required
                      className="pr-10"
                  />
                  <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                        <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                        <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
              </div>
            </div>

            <Button
                variant="outline"
                className="w-full flex items-center justify-center gap-2"
                onClick={handleGoogleLogin}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M15.5453 6.54545H8.18177V9.63636H12.3635C12.0908 11.6 10.4544 12.7273 8.18177 12.7273C5.52722 12.7273 3.36359 10.5636 3.36359 7.90909C3.36359 5.25455 5.52722 3.09091 8.18177 3.09091C9.38177 3.09091 10.4544 3.52727 11.2726 4.25455L13.6362 1.89091C12.1817 0.545455 10.2908 -0.0909091 8.18177 -0.0909091C3.81813 -0.0909091 0.181763 3.54545 0.181763 7.90909C0.181763 12.2727 3.81813 15.9091 8.18177 15.9091C12.1817 15.9091 15.8181 12.8182 15.8181 7.90909C15.8181 7.45455 15.7271 6.98182 15.5453 6.54545Z"
                    fill="#4285F4"
                />
                <path
                    d="M1.45459 4.72727L4.18186 6.72727C4.90913 4.72727 6.36368 3.09091 8.18186 3.09091C9.38186 3.09091 10.4546 3.52727 11.2728 4.25455L13.6364 1.89091C12.1819 0.545455 10.291 -0.0909091 8.18186 -0.0909091C5.27277 -0.0909091 2.72732 1.89091 1.45459 4.72727Z"
                    fill="#EA4335"
                />
                <path
                    d="M8.18182 15.9091C10.2909 15.9091 12.1818 15.3091 13.6727 13.9636L11.0909 11.7818C10.3273 12.3455 9.34545 12.7273 8.18182 12.7273C5.92727 12.7273 3.99091 11.6 3.7 9.63636H0.981818V11.8182C2.23636 14.3636 5.01818 15.9091 8.18182 15.9091Z"
                    fill="#34A853"
                />
                <path
                    d="M3.7 9.63636C3.52727 9.09091 3.45455 8.50909 3.45455 7.90909C3.45455 7.30909 3.52727 6.72727 3.7 6.18182V4H0.981818C0.436364 5.16364 0.181818 6.50909 0.181818 7.90909C0.181818 9.30909 0.436364 10.6545 0.981818 11.8182L3.7 9.63636Z"
                    fill="#FBBC05"
                />
              </svg>
              Continue with Google
            </Button>

            <div className="mt-6 p-4 bg-muted rounded-lg">
              <h3 className="font-semibold mb-2 text-sm">Staff Access Only</h3>
              <p className="text-xs text-muted-foreground">
                This login is for restaurant staff only. Staff accounts are managed by the administrator. If you're a
                customer, please use the regular menu to place orders.
              </p>
            </div>

            <div className="mt-4 text-center space-y-2">
              <Button variant="outline" asChild className="w-full">
                <a href="/">Back to Menu</a>
              </Button>
              <Button variant="ghost" asChild className="w-full">
                <a href="/login">Customer Login</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
