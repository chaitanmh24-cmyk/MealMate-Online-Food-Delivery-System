import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Button, ListGroup, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

const Cart = () => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useContext(AuthContext);
    const navigate = useNavigate();

    const fetchCart = async () => {
        try {
            const res = await api.get('cart/');
            setCart(res.data);
        } catch (err) {
            console.error("Error fetching cart", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchCart();
        else {
            setLoading(false);
            navigate('/login');
        }
    }, [user]);

    const handleRemove = async (itemId) => {
        try {
            await api.delete(`cart-items/${itemId}/`);
            fetchCart();
        } catch (err) {
            console.error("Error removing item", err);
        }
    };

    const handleCheckout = async () => {
        try {
            // Need to place order
            await api.post('orders/', {});
            alert("Order placed successfully!");
            navigate('/dashboard');
        } catch (err) {
            console.error("Error placing order", err);
            alert("Failed to place order.");
        }
    };

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;

    if (!cart || !cart.items || cart.items.length === 0) {
        return (
            <Container className="text-center mt-5">
                <Card className="premium-card p-5">
                    <h2 className="text-muted">Your Cart is Empty 🛒</h2>
                    <Button variant="primary" className="mt-3 mx-auto" style={{ width: '200px' }} onClick={() => navigate('/')}>
                        Browse Foods
                    </Button>
                </Card>
            </Container>
        );
    }

    return (
        <Container className="mt-5">
            <h2 className="mb-4 fw-bold">Your Cart</h2>
            <Row>
                <Col md={8}>
                    <Card className="premium-card border-0 mb-4">
                        <ListGroup variant="flush">
                            {cart.items.map(item => (
                                <ListGroup.Item key={item.id} className="p-4 d-flex align-items-center">
                                    <div style={{ width: '80px', height: '80px', borderRadius: '8px', overflow: 'hidden', marginRight: '15px', backgroundColor: '#f8f9fa' }}>
                                        {item.food_item_details?.image ? (
                                            <img src={item.food_item_details.image} alt={item.food_item_details.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                        ) : (
                                            <div className="d-flex align-items-center justify-content-center h-100"><small>No Img</small></div>
                                        )}
                                    </div>
                                    <div className="flex-grow-1">
                                        <h5 className="fw-bold mb-1">{item.food_item_details?.name}</h5>
                                        <div className="text-muted small">₹{item.food_item_details?.price} x {item.quantity}</div>
                                    </div>
                                    <div className="text-end">
                                        <h5 className="fw-bold text-primary mb-2">₹{item.food_item_details?.price * item.quantity}</h5>
                                        <Button variant="outline-danger" size="sm" onClick={() => handleRemove(item.id)}>Remove</Button>
                                    </div>
                                </ListGroup.Item>
                            ))}
                        </ListGroup>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card className="premium-card border-0 p-4 sticky-top" style={{ top: '100px' }}>
                        <h4 className="fw-bold mb-4">Order Summary</h4>
                        <div className="d-flex justify-content-between mb-2">
                            <span className="text-muted">Subtotal</span>
                            <span className="fw-bold">₹{cart.total_price}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                            <span className="text-muted">Delivery Fee</span>
                            <span className="fw-bold text-success">Free</span>
                        </div>
                        <hr />
                        <div className="d-flex justify-content-between mb-4">
                            <span className="fw-bold fs-5">Total</span>
                            <span className="fw-bold fs-5 text-primary">₹{cart.total_price}</span>
                        </div>
                        <Button 
                            variant="primary" 
                            size="lg" 
                            className="w-100" 
                            style={{ backgroundColor: 'var(--primary)', border: 'none' }}
                            onClick={handleCheckout}
                        >
                            Proceed to Checkout
                        </Button>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Cart;
