import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Button, ListGroup, Spinner, Badge, Alert } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

const Cart = () => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);
    const [orderPlacing, setOrderPlacing] = useState(false);
    const [orderSuccess, setOrderSuccess] = useState(false);
    const [error, setError] = useState(null);
    const { user } = useContext(AuthContext);
    const navigate = useNavigate();

    const fetchCart = async () => {
        try {
            const res = await api.get('cart/');
            // cart/ returns a list from ModelViewSet or single object depending on get_object
            if (Array.isArray(res.data)) {
                setCart(res.data.length > 0 ? res.data[0] : null);
            } else {
                setCart(res.data);
            }
        } catch (err) {
            console.error("Error fetching cart", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) {
            fetchCart();
        } else {
            setLoading(false);
            navigate('/login');
        }
    }, [user]);

    const handleUpdateQuantity = async (itemId, newQty) => {
        if (newQty <= 0) {
            handleRemove(itemId);
            return;
        }
        setUpdatingId(itemId);
        try {
            await api.patch(`cart-items/${itemId}/`, { quantity: newQty });
            await fetchCart();
        } catch (err) {
            console.error("Error updating quantity", err);
        } finally {
            setUpdatingId(null);
        }
    };

    const handleRemove = async (itemId) => {
        setUpdatingId(itemId);
        try {
            await api.delete(`cart-items/${itemId}/`);
            await fetchCart();
        } catch (err) {
            console.error("Error removing item", err);
        } finally {
            setUpdatingId(null);
        }
    };

    const handleCheckout = async () => {
        setOrderPlacing(true);
        setError(null);
        try {
            await api.post('orders/', {});
            setOrderSuccess(true);
            setTimeout(() => {
                navigate('/dashboard');
            }, 1800);
        } catch (err) {
            console.error("Error placing order", err);
            setError(err.response?.data?.error || "Failed to place order. Please try again.");
            setOrderPlacing(false);
        }
    };

    if (loading) {
        return (
            <Container className="text-center py-5">
                <Spinner animation="border" variant="danger" />
                <p className="mt-3 text-muted">Loading your cart...</p>
            </Container>
        );
    }

    if (orderSuccess) {
        return (
            <Container className="py-5 text-center">
                <Card className="border-0 shadow-sm p-5 mx-auto" style={{ maxWidth: '500px', borderRadius: '16px' }}>
                    <div style={{ fontSize: '4rem' }}>🎉</div>
                    <h3 className="fw-bold mt-3 text-success">Order Placed Successfully!</h3>
                    <p className="text-muted">Your delicious food is being prepared. Redirecting to your dashboard...</p>
                    <Spinner animation="border" size="sm" variant="success" className="mx-auto" />
                </Card>
            </Container>
        );
    }

    if (!cart || !cart.items || cart.items.length === 0) {
        return (
            <Container className="py-5 text-center">
                <Card className="border-0 shadow-sm p-5 mx-auto" style={{ maxWidth: '520px', borderRadius: '16px' }}>
                    <div style={{ fontSize: '4rem' }}>🛒</div>
                    <h3 className="fw-bold mt-3">Your Cart is Empty</h3>
                    <p className="text-muted">Looks like you haven't added any mouth-watering dishes yet.</p>
                    <Button 
                        as={Link} 
                        to="/" 
                        className="fw-bold px-4 py-2 mt-2 mx-auto"
                        style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)', borderRadius: '25px', width: 'fit-content' }}
                    >
                        Explore Menu & Foods
                    </Button>
                </Card>
            </Container>
        );
    }

    const totalItemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);

    return (
        <Container className="py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold mb-1">Your Food Cart 🛒</h2>
                    <p className="text-muted mb-0">{totalItemCount} item{totalItemCount !== 1 ? 's' : ''} in your order</p>
                </div>
                <Button as={Link} to="/" variant="outline-secondary" size="sm" style={{ borderRadius: '20px' }}>
                    + Add More Items
                </Button>
            </div>

            {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}

            <Row className="g-4">
                <Col lg={8}>
                    <Card className="border-0 shadow-sm" style={{ borderRadius: '16px', overflow: 'hidden' }}>
                        <ListGroup variant="flush">
                            {cart.items.map(item => {
                                const food = item.food_item_details;
                                const isUpdating = updatingId === item.id;
                                return (
                                    <ListGroup.Item key={item.id} className="p-3 p-md-4">
                                        <div className="d-flex align-items-center gap-3">
                                            {/* Food Image */}
                                            <div style={{ width: '90px', height: '90px', minWidth: '90px', borderRadius: '12px', overflow: 'hidden', backgroundColor: '#f1f2f6' }}>
                                                <img 
                                                    src={food?.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'} 
                                                    alt={food?.name} 
                                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                    onError={(e) => {
                                                        e.target.onerror = null;
                                                        e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500';
                                                    }}
                                                />
                                            </div>

                                            {/* Info */}
                                            <div className="flex-grow-1">
                                                <div className="d-flex align-items-center gap-2 mb-1">
                                                    <h5 className="fw-bold mb-0">{food?.name}</h5>
                                                    <Badge bg={food?.veg_nonveg === 'Veg' ? 'success' : 'danger'} style={{ fontSize: '0.65rem' }}>
                                                        {food?.veg_nonveg}
                                                    </Badge>
                                                </div>
                                                <div className="text-muted small mb-2">
                                                    ₹{food?.price} each
                                                </div>

                                                {/* Quantity controls */}
                                                <div className="d-flex align-items-center gap-2">
                                                    <div className="d-flex align-items-center border rounded-pill px-2 py-1 bg-light">
                                                        <button 
                                                            className="btn btn-link btn-sm text-dark p-0 px-1 text-decoration-none fw-bold"
                                                            disabled={isUpdating}
                                                            onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                                                        >
                                                            −
                                                        </button>
                                                        <span className="mx-2 fw-bold text-center" style={{ minWidth: '20px' }}>
                                                            {item.quantity}
                                                        </span>
                                                        <button 
                                                            className="btn btn-link btn-sm text-dark p-0 px-1 text-decoration-none fw-bold"
                                                            disabled={isUpdating}
                                                            onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                                        >
                                                            +
                                                        </button>
                                                    </div>

                                                    <Button 
                                                        variant="link" 
                                                        size="sm" 
                                                        className="text-danger p-0 ms-2 text-decoration-none small"
                                                        disabled={isUpdating}
                                                        onClick={() => handleRemove(item.id)}
                                                    >
                                                        🗑️ Remove
                                                    </Button>
                                                </div>
                                            </div>

                                            {/* Subtotal */}
                                            <div className="text-end" style={{ minWidth: '90px' }}>
                                                <h5 className="fw-bold mb-0" style={{ color: 'var(--primary)' }}>
                                                    ₹{Number(food?.price || 0) * item.quantity}
                                                </h5>
                                            </div>
                                        </div>
                                    </ListGroup.Item>
                                );
                            })}
                        </ListGroup>
                    </Card>
                </Col>

                {/* Summary */}
                <Col lg={4}>
                    <Card className="border-0 shadow-sm p-4 sticky-top" style={{ top: '90px', borderRadius: '16px' }}>
                        <h4 className="fw-bold mb-3">Order Summary</h4>
                        
                        <div className="d-flex justify-content-between mb-2">
                            <span className="text-muted">Items Subtotal ({totalItemCount})</span>
                            <span className="fw-bold">₹{cart.total_price}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                            <span className="text-muted">Delivery Charges</span>
                            <span className="fw-bold text-success">FREE</span>
                        </div>
                        <div className="d-flex justify-content-between mb-3">
                            <span className="text-muted">Packaging & Taxes</span>
                            <span className="fw-bold text-success">₹0</span>
                        </div>
                        
                        <hr />
                        
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <span className="fw-bold fs-5">Grand Total</span>
                                <div className="text-muted" style={{ fontSize: '0.75rem' }}>Inclusive of all taxes</div>
                            </div>
                            <span className="fw-bold fs-4" style={{ color: 'var(--primary)' }}>
                                ₹{cart.total_price}
                            </span>
                        </div>

                        <Button 
                            variant="primary" 
                            size="lg" 
                            className="w-100 fw-bold py-3 shadow-sm"
                            disabled={orderPlacing}
                            style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)', borderRadius: '12px' }}
                            onClick={handleCheckout}
                        >
                            {orderPlacing ? (
                                <>
                                    <Spinner animation="border" size="sm" className="me-2" />
                                    Placing Order...
                                </>
                            ) : (
                                '🛵 Place Order Now'
                            )}
                        </Button>

                        <div className="d-flex align-items-center justify-content-center gap-2 mt-3 text-muted small">
                            <span>🔒</span> <span>Safe and Secure Checkout</span>
                        </div>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Cart;
