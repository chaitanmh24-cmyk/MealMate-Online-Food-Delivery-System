import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Badge, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../services/api';
import useSEO from '../hooks/useSEO';

const vegBadgeColor = (type) => {
    if (type === 'Veg') return 'success';
    if (type === 'Non-Veg') return 'danger';
    return 'warning';
};

const Home = () => {
    useSEO('Home', 'Discover the best food and drinks in your city with MealMate.');
    const [foods, setFoods] = useState([]);
    const [restaurants, setRestaurants] = useState([]);
    const [search, setSearch] = useState('');
    const [activeFilter, setActiveFilter] = useState('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [foodRes, restRes] = await Promise.all([
                    api.get('restaurants/foods/'),
                    api.get('restaurants/restaurants/'),
                ]);
                setFoods(foodRes.data);
                setRestaurants(restRes.data);
            } catch (error) {
                console.error("Error fetching data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const filteredFoods = foods.filter(f => {
        const matchSearch = f.name.toLowerCase().includes(search.toLowerCase()) ||
            f.restaurant_name?.toLowerCase().includes(search.toLowerCase());
        if (activeFilter === 'veg') return matchSearch && f.veg_nonveg === 'Veg';
        if (activeFilter === 'nonveg') return matchSearch && f.veg_nonveg === 'Non-Veg';
        return matchSearch;
    });

    const recommendedFoods = foods.slice(0, 4);

    const renderFoodCard = (food) => (
        <Col md={4} lg={3} className="mb-4" key={food.id}>
            <Card className="premium-card h-100 hover-scale">
                <div style={{ height: '200px', backgroundColor: '#f1f2f6', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                    {food.image ? (
                        <img src={food.image} alt={food.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <span style={{ fontSize: '3rem' }}>🍽️</span>
                    )}
                </div>
                <Card.Body className="d-flex flex-column">
                    <div className="d-flex justify-content-between align-items-start mb-1">
                        <Card.Title className="fw-bold mb-0 fs-6">{food.name}</Card.Title>
                        <Badge bg={food.veg_nonveg === 'Veg' ? 'success' : 'danger'} style={{ fontSize: '0.65rem' }}>{food.veg_nonveg}</Badge>
                    </div>
                    <Card.Text className="text-muted" style={{ fontSize: '0.8rem' }}>
                        🏪 {food.restaurant_name}
                        {food.restaurant_location && <><br />📍 {food.restaurant_location}</>}
                    </Card.Text>
                    <div className="d-flex justify-content-between align-items-center mt-auto">
                        <h5 className="mb-0 fw-bold" style={{ color: 'var(--primary)' }}>₹{food.price}</h5>
                        <Button variant="outline-primary" size="sm" as={Link} to={`/food/${food.id}`} style={{ borderColor: 'var(--primary)', color: 'var(--primary)' }}>View</Button>
                    </div>
                </Card.Body>
            </Card>
        </Col>
    );

    const renderRestaurantCard = (rest) => (
        <Col md={4} lg={3} className="mb-4" key={rest.id}>
            <Card className="premium-card h-100 hover-scale">
                <div style={{ height: '180px', backgroundColor: '#f1f2f6', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {rest.image ? (
                        <img src={rest.image} alt={rest.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <span style={{ fontSize: '3rem' }}>🏪</span>
                    )}
                </div>
                <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-1">
                        <Card.Title className="fw-bold mb-0 fs-6">{rest.name}</Card.Title>
                        <Badge bg={vegBadgeColor(rest.veg_nonveg)} style={{ fontSize: '0.65rem' }}>{rest.veg_nonveg}</Badge>
                    </div>
                    {rest.location && <p className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>📍 {rest.location}</p>}
                    <p className="text-muted mb-0" style={{ fontSize: '0.8rem' }}>{rest.food_items?.length || 0} items available</p>
                </Card.Body>
            </Card>
        </Col>
    );

    return (
        <div>
            {/* Hero Section */}
            <div className="text-white text-center py-5 mb-5" style={{ background: 'linear-gradient(135deg, var(--primary) 0%, #ff7b8f 100%)' }}>
                <Container>
                    <h1 className="display-4 fw-bold mb-2">Craving Something Delicious?</h1>
                    <p className="lead mb-4 opacity-75">Discover the best food and drinks in your city</p>
                    <Row className="justify-content-center">
                        <Col md={7}>
                            <div className="glassmorphism p-2 d-flex gap-2 rounded-pill" style={{ background: 'rgba(255,255,255,0.2)' }}>
                                <Form.Control
                                    type="search"
                                    placeholder="Search dishes or restaurants..."
                                    className="border-0 shadow-none rounded-pill"
                                    style={{ background: 'rgba(255,255,255,0.9)', color: '#333' }}
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                />
                                <Button style={{ backgroundColor: 'var(--secondary)', border: 'none', borderRadius: '50px', paddingLeft: '20px', paddingRight: '20px' }}>
                                    🔍
                                </Button>
                            </div>
                        </Col>
                    </Row>
                    {/* Filter Chips */}
                    <div className="d-flex justify-content-center gap-2 mt-4 flex-wrap">
                        {[['all', 'All', '🍽️'], ['veg', 'Veg Only', '🥦'], ['nonveg', 'Non-Veg', '🍗']].map(([val, label, icon]) => (
                            <Button key={val} size="sm" onClick={() => setActiveFilter(val)}
                                style={{
                                    background: activeFilter === val ? 'white' : 'rgba(255,255,255,0.2)',
                                    color: activeFilter === val ? 'var(--primary)' : 'white',
                                    border: 'none',
                                    borderRadius: '50px',
                                    fontWeight: activeFilter === val ? '700' : '400',
                                    transition: 'all 0.2s ease'
                                }}>
                                {icon} {label}
                            </Button>
                        ))}
                    </div>
                </Container>
            </div>

            <Container>
                {loading ? (
                    <div className="text-center py-5"><Spinner animation="border" style={{ color: 'var(--primary)' }} /></div>
                ) : (
                    <>
                        {/* Restaurants Section */}
                        {!search && restaurants.length > 0 && (
                            <div className="mb-5">
                                <h3 className="fw-bold mb-4">🏪 Restaurants Near You</h3>
                                <Row>
                                    {restaurants.map(renderRestaurantCard)}
                                </Row>
                            </div>
                        )}

                        {/* Recommendations */}
                        {!search && activeFilter === 'all' && recommendedFoods.length > 0 && (
                            <div className="mb-5">
                                <h3 className="fw-bold mb-4">✨ Recommended For You</h3>
                                <Row>{recommendedFoods.map(renderFoodCard)}</Row>
                            </div>
                        )}

                        {/* All Foods */}
                        <h3 className="fw-bold mb-4">{search ? `Results for "${search}"` : 'Popular Dishes'}</h3>
                        <Row>
                            {filteredFoods.map(renderFoodCard)}
                            {filteredFoods.length === 0 && (
                                <Col className="text-center py-5">
                                    <p style={{ fontSize: '4rem' }}>🔍</p>
                                    <p className="text-muted fs-5">No results found. Try a different search.</p>
                                </Col>
                            )}
                        </Row>
                    </>
                )}
            </Container>
        </div>
    );
};

export default Home;
