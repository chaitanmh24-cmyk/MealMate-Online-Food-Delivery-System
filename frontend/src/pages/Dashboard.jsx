import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Badge, ListGroup, Spinner } from 'react-bootstrap';
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
                setOrders(res.data);
            } catch (err) {
                console.error("Error fetching orders", err);
            } finally {
                setLoading(false);
            }
        };
        if (user) fetchOrders();
    }, [user]);

    if (!user) return <Container className="mt-5"><h2>Please login to view dashboard.</h2></Container>;
    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;

    return (
        <Container className="mt-5">
            <h2 className="mb-4 fw-bold">My Dashboard</h2>
            <Row>
                <Col md={4} className="mb-4">
                    <Card className="premium-card p-4 text-center border-0">
                        <div className="mb-3">
                            <div style={{ width: '100px', height: '100px', borderRadius: '50%', backgroundColor: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto', fontSize: '2rem', fontWeight: 'bold' }}>
                                {user.username.charAt(0).toUpperCase()}
                            </div>
                        </div>
                        <h4 className="fw-bold">{user.first_name} {user.last_name}</h4>
                        <p className="text-muted mb-1">@{user.username}</p>
                        <p className="text-muted">{user.email}</p>
                        <Badge bg="info" className="fs-6 mt-2">{user.role}</Badge>
                    </Card>
                </Col>
                <Col md={8}>
                    <Card className="premium-card p-4 border-0">
                        <h4 className="fw-bold mb-4">Order History</h4>
                        {orders.length === 0 ? (
                            <p className="text-muted">You haven't placed any orders yet.</p>
                        ) : (
                            <ListGroup variant="flush">
                                {orders.map(order => (
                                    <ListGroup.Item key={order.id} className="px-0 py-3">
                                        <div className="d-flex justify-content-between align-items-center mb-2">
                                            <h6 className="fw-bold mb-0">Order #{order.id}</h6>
                                            <Badge bg={order.status === 'Delivered' ? 'success' : order.status === 'Cancelled' ? 'danger' : 'warning'}>
                                                {order.status}
                                            </Badge>
                                        </div>
                                        <p className="text-muted small mb-2">Placed on: {new Date(order.created_at).toLocaleString()}</p>
                                        <div className="d-flex justify-content-between align-items-center">
                                            <div className="text-muted small">
                                                {order.items?.map(i => `${i.quantity}x ${i.food_item_details?.name}`).join(', ')}
                                            </div>
                                            <h6 className="fw-bold text-primary mb-0">₹{order.total_amount}</h6>
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
