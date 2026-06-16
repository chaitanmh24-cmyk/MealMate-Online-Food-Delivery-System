import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Badge, Spinner } from 'react-bootstrap';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import useSEO from '../hooks/useSEO';

const FoodDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const [food, setFood] = useState(null);
    const [loading, setLoading] = useState(true);

    useSEO(food ? food.name : 'Food Details', food ? food.description : 'Details about this food item.');

    useEffect(() => {
        const fetchFood = async () => {
            try {
                const res = await api.get(`restaurants/foods/${id}/`);
                setFood(res.data);
            } catch (err) {
                console.error("Error fetching food details", err);
            } finally {
                setLoading(false);
            }
        };
        fetchFood();
    }, [id]);

    const addToCart = async () => {
        if (!user) {
            navigate('/login');
            return;
        }
        try {
            await api.post('cart-items/', { food_item: id, quantity: 1 });
            alert("Added to cart!");
            navigate('/cart');
        } catch (err) {
            console.error("Error adding to cart", err);
            alert("Failed to add to cart.");
        }
    };

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;
    if (!food) return <Container className="mt-5"><h2>Food not found</h2></Container>;

    return (
        <Container className="mt-5">
            <Card className="premium-card p-4 shadow-sm border-0">
                <Row>
                    <Col md={6}>
                        <div style={{ height: '400px', backgroundColor: '#f8f9fa', borderRadius: '12px', overflow: 'hidden' }}>
                            {food.image ? (
                                <img src={food.image} alt={food.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                                <div className="d-flex align-items-center justify-content-center h-100 text-muted">
                                    No Image Available
                                </div>
                            )}
                        </div>
                    </Col>
                    <Col md={6} className="d-flex flex-column justify-content-center mt-4 mt-md-0 pl-md-4">
                        <Badge bg={food.veg_nonveg === 'Veg' ? 'success' : 'danger'} className="align-self-start mb-2 fs-6">
                            {food.veg_nonveg}
                        </Badge>
                        <h1 className="fw-bold" style={{ color: 'var(--text)' }}>{food.name}</h1>
                        <h4 className="text-muted">{food.restaurant_name} • {food.category_name}</h4>
                        
                        <div className="my-4">
                            <h2 className="text-primary fw-bold">₹{food.price}</h2>
                        </div>
                        
                        <p className="text-muted mb-4" style={{ fontSize: '1.1rem' }}>
                            {food.description || "No description available for this item."}
                        </p>

                        <div className="d-grid gap-2 mt-auto">
                            <Button 
                                variant="primary" 
                                size="lg" 
                                style={{ backgroundColor: 'var(--primary)', border: 'none', padding: '15px' }}
                                onClick={addToCart}
                            >
                                Add to Cart 🛒
                            </Button>
                        </div>
                    </Col>
                </Row>
            </Card>
        </Container>
    );
};

export default FoodDetails;
