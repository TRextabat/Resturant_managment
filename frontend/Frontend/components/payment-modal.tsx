"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CreditCard, Check } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiClient } from "@/lib/api"

interface PaymentModalProps {
    isOpen: boolean
    onClose: () => void
    order: any
    currentUser: any
    onPaymentSuccess: () => void
}

export function PaymentModal({ isOpen, onClose, order, currentUser, onPaymentSuccess }: PaymentModalProps) {
    const [selectedCard, setSelectedCard] = useState<string | null>(null)
    const [isProcessing, setIsProcessing] = useState(false)
    const { toast } = useToast()

    // Mock saved card data
    const savedCards = [
        {
            id: "card_1",
            last4: "4242",
            brand: "Visa",
            expiry: "12/25",
        },
    ]

    const handlePayment = async () => {
        if (!selectedCard) {
            toast({
                title: "No payment method selected",
                description: "Please select a payment method to continue.",
                variant: "destructive",
            })
            return
        }

        setIsProcessing(true)

        try {
            const paymentData = {
                order_id: order.id,
                customer_id: currentUser.id,
                amount: Number.parseFloat(order.total_amount),
                method: "card" as const,
                is_successful: true,
            }

            const response = await apiClient.createPayment(paymentData)

            if (response.error) {
                toast({
                    title: "Payment failed",
                    description: response.error,
                    variant: "destructive",
                })
            } else {
                toast({
                    title: "Payment successful!",
                    description: `Your payment of ₺${order.total_amount} has been processed.`,
                })
                onPaymentSuccess()
                onClose()
            }
        } catch (error) {
            toast({
                title: "Payment error",
                description: "An unexpected error occurred during payment processing.",
                variant: "destructive",
            })
        } finally {
            setIsProcessing(false)
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle>Pay for Order</DialogTitle>
                    <DialogDescription>Complete your payment for Order #{order?.id?.slice(0, 8)}</DialogDescription>
                </DialogHeader>

                <div className="space-y-6">
                    {/* Order Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-sm">Order Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2 text-sm">
                                {order?.items?.map((item: any) => (
                                    <div key={item.menu_item_id} className="flex justify-between">
                    <span>
                      {item.quantity}x {item.item_name}
                    </span>
                                        <span>₺{item.line_total}</span>
                                    </div>
                                ))}
                                <div className="border-t pt-2 font-semibold">
                                    <div className="flex justify-between">
                                        <span>Total:</span>
                                        <span>₺{order?.total_amount}</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Payment Method Selection */}
                    <div>
                        <h3 className="text-sm font-medium mb-3">Select Payment Method</h3>
                        <div className="space-y-2">
                            {savedCards.map((card) => (
                                <Card
                                    key={card.id}
                                    className={`cursor-pointer transition-colors ${
                                        selectedCard === card.id ? "border-primary bg-primary/5" : "hover:border-muted-foreground/50"
                                    }`}
                                    onClick={() => setSelectedCard(card.id)}
                                >
                                    <CardContent className="flex items-center justify-between p-4">
                                        <div className="flex items-center space-x-3">
                                            <CreditCard className="h-5 w-5 text-muted-foreground" />
                                            <div>
                                                <div className="font-medium">
                                                    {card.brand} •••• {card.last4}
                                                </div>
                                                <div className="text-sm text-muted-foreground">Expires {card.expiry}</div>
                                            </div>
                                        </div>
                                        {selectedCard === card.id && <Check className="h-5 w-5 text-primary" />}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </div>

                    {/* Payment Actions */}
                    <div className="flex space-x-3">
                        <Button variant="outline" onClick={onClose} className="flex-1">
                            Cancel
                        </Button>
                        <Button onClick={handlePayment} disabled={!selectedCard || isProcessing} className="flex-1">
                            {isProcessing ? "Processing..." : `Pay ₺${order?.total_amount}`}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
