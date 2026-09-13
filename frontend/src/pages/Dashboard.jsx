import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Badge, ListGroup, Spinner, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const Dashboard = () => {
    const { user } = useContext(AuthContext);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const res = await api.get('orders/');
                setOrders(Array.isArray(res.data) ? res.data : []);
            } catch (err) {
                console.error("Error fetching orders", err);
            } finally {
                setLoading(false);
            }
        };
        if (user) fetchOrders();
    }, [user]);

    if (!user) {
        return (
            <Container className="text-center py-5">
                <h3>Please log in to view your dashboard.</h3>
                <Button as={Link} to="/login" variant="primary" className="mt-3">
                    Sign In
                </Button>
            </Container>
        );
    }

    if (loading) {
        return (
            <Container className="text-center py-5">
                <Spinner animation="border" variant="danger" />
                <p className="mt-3 text-muted">Loading your dashboard...</p>
            </Container>
        );
    }

    const totalSpent = orders.reduce((sum, o) => sum + Number(o.total_amount || 0), 0);

    const getStatusVariant = (status) => {
        switch (status) {
            case 'Delivered': return 'success';
            case 'Cancelled': return 'danger';
            case 'Out for Delivery': return 'info';
            case 'Preparing': return 'primary';
            case 'Confirmed': return 'warning';
            default: return 'secondary';
        }
    };

    return (
        <Container className="py-4">
            <h2 className="fw-bold mb-4">My Account & Orders 📋</h2>
            <Row className="g-4">
                {/* Profile Card */}
                <Col md={4}>
                    <Card className="border-0 shadow-sm p-4 text-center" style={{ borderRadius: '16px' }}>
                        <div className="mb-3">
                            <div style={{
                                width: '90px',
                                height: '90px',
                                borderRadius: '50%',
                                background: 'linear-gradient(135deg, #ff4757 0%, #ff6b81 100%)',
                                color: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                margin: '0 auto',
                                fontSize: '2.2rem',
                                fontWeight: 'bold',
                                boxShadow: '0 8px 16px rgba(255, 71, 87, 0.25)'
                            }}>
                                {user.username.charAt(0).toUpperCase()}
                            </div>
                        </div>

                        <h4 className="fw-bold mb-1">
                            {user.first_name || user.last_name ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : user.username}
                        </h4>
                        <p className="text-muted small mb-1">@{user.username}</p>
                        <p className="text-muted small mb-3">{user.email}</p>

                        <div>
                            <Badge bg={user.role === 'Admin' ? 'danger' : 'primary'} className="px-3 py-2 fs-6">
                                {user.role === 'Admin' ? '👑 Admin' : '👤 Customer'}
                            </Badge>
                        </div>

                        <hr className="my-4" />

                        {/* Quick metrics */}
                        <Row className="text-center">
                            <Col xs={6} className="border-end">
                                <h4 className="fw-bold mb-0 text-dark">{orders.length}</h4>
                                <small className="text-muted">Total Orders</small>
                            </Col>
                            <Col xs={6}>
                                <h4 className="fw-bold mb-0" style={{ color: 'var(--primary)' }}>₹{totalSpent}</h4>
                                <small className="text-muted">Total Spent</small>
                            </Col>
                        </Row>

                        {user.role === 'Admin' && (
                            <div className="mt-4">
                                <Button as={Link} to="/admin" variant="outline-danger" className="w-100 fw-bold">
                                    ⚙️ Go to Admin Portal
                                </Button>
                            </div>
                        )}
                    </Card>
                </Col>

                {/* Orders List */}
                <Col md={8}>
                    <Card className="border-0 shadow-sm p-4" style={{ borderRadius: '16px' }}>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <h4 className="fw-bold mb-0">Order History</h4>
                            <span className="text-muted small">{orders.length} orders placed</span>
                        </div>

                        {orders.length === 0 ? (
                            <div className="text-center py-5">
                                <div style={{ fontSize: '3rem' }}>🍽️</div>
                                <h5 className="fw-bold mt-2">No Orders Yet</h5>
                                <p className="text-muted">You haven't placed any food orders yet.</p>
                                <Button as={Link} to="/" style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)', borderRadius: '20px' }}>
                                    Explore Menu
                                </Button>
                            </div>
                        ) : (
                            <ListGroup variant="flush">
                                {orders.map(order => (
                                    <ListGroup.Item key={order.id} className="px-0 py-3 border-bottom">
                                        <div className="d-flex justify-content-between align-items-start mb-2">
                                            <div>
                                                <span className="fw-bold fs-6">Order #{order.id}</span>
                                                <div className="text-muted small">
                                                    📅 {new Date(order.created_at).toLocaleDateString()} at {new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </div>
                                            </div>
                                            <Badge bg={getStatusVariant(order.status)} className="px-3 py-2 text-capitalize">
                                                {order.status}
                                            </Badge>
                                        </div>

                                        {/* Order Items */}
                                        <div className="bg-light p-3 rounded my-2">
                                            {order.items && order.items.length > 0 ? (
                                                order.items.map((item, idx) => (
                                                    <div key={idx} className="d-flex justify-content-between align-items-center py-1 small">
                                                        <span>
                                                            <span className="fw-bold text-dark">{item.quantity}x</span> {item.food_item_details?.name || 'Food Item'}
                                                        </span>
                                                        <span className="text-muted">
                                                            ₹{Number(item.price || item.food_item_details?.price || 0) * item.quantity}
                                                        </span>
                                                    </div>
                                                ))
                                            ) : (
                                                <span className="text-muted small">Meal items</span>
                                            )}
                                        </div>

                                        <div className="d-flex justify-content-between align-items-center mt-2">
                                            <span className="text-muted small">
                                                Delivery Status: <strong>{order.status}</strong>
                                            </span>
                                            <div className="text-end">
                                                <span className="text-muted small me-2">Total Amount:</span>
                                                <span className="fw-bold fs-5" style={{ color: 'var(--primary)' }}>
                                                    ₹{order.total_amount}
                                                </span>
                                            </div>
                                        </div>
                                    </ListGroup.Item>
                                ))}
                            </ListGroup>
                        )}
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Dashboard;
