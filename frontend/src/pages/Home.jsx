import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Form, Button, Badge, Spinner, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import useSEO from '../hooks/useSEO';
import { AuthContext } from '../context/AuthContext';

// Helper categorization functions
export const isColdDrink = (food) => {
    const cat = (food.category_name || '').toLowerCase();
    const cuisine = (food.cuisine_type || '').toLowerCase();
    const name = (food.name || '').toLowerCase();
    return cat.includes('cold drink') || 
           cuisine.includes('cold drink') || 
           cuisine.includes('diet drink') || 
           /coca-cola|pepsi|sprite|coke|fanta|drink|beverage|soda/i.test(name);
};

export const isIceCream = (food) => {
    const cat = (food.category_name || '').toLowerCase();
    const cuisine = (food.cuisine_type || '').toLowerCase();
    const name = (food.name || '').toLowerCase();
    return cat.includes('ice cream') || 
           /ice cream|cornetto|tricone|cone|sundae|butterscotch|vanilla cup|chocolate cup|mississippi mud|baskin robbins|havmor|naturals/i.test(name) ||
           cuisine.includes('ice cream');
};

export const isVeg = (food) => {
    return food.veg_nonveg === 'Veg' && !isColdDrink(food) && !isIceCream(food);
};

export const isNonVeg = (food) => {
    return food.veg_nonveg === 'Non-Veg';
};

export const isRecommended = (food) => {
    const recommendedDishes = [
        'butter chicken',
        'paneer butter masala',
        'chicken biryani',
        'chicken dum biryani',
        'masala dosa',
        'misal pav',
        'cornetto',
        'tricone',
        'coca-cola',
        'chole bhature',
        'fish curry',
        'mississippi mud',
        'tender coconut'
    ];
    const hasReview = food.reviews && food.reviews.length > 0;
    const isTopDish = recommendedDishes.some(dish => (food.name || '').toLowerCase().includes(dish));
    return hasReview || isTopDish;
};

export const getItemBadge = (food) => {
    if (isIceCream(food)) {
        return { label: 'Ice Cream', className: 'badge-icecream', icon: '🍦' };
    }
    if (isColdDrink(food)) {
        return { label: 'Cold Drink', className: 'badge-colddrink', icon: '🥤' };
    }
    if (food.veg_nonveg === 'Veg') {
        return { label: 'Veg', className: 'badge-veg', icon: '🥦' };
    }
    return { label: 'Non-Veg', className: 'badge-nonveg', icon: '🍗' };
};

const vegBadgeColor = (type) => {
    if (type === 'Veg') return 'success';
    if (type === 'Non-Veg') return 'danger';
    return 'warning';
};

const CATEGORIES_CONFIG = [
    { id: 'all', label: 'All Dishes', icon: '🍽️', desc: 'Explore all menu items', color: '#ff4757', bg: '#ffebee' },
    { id: 'recommended', label: 'Recommendations', icon: '⭐', desc: "Chef's curated favorites", color: '#ffa502', bg: '#fff8e1' },
    { id: 'veg', label: 'Veg', icon: '🥦', desc: '100% Pure vegetarian dishes', color: '#2ed573', bg: '#e8faf0' },
    { id: 'nonveg', label: 'Non-Veg', icon: '🍗', desc: 'Tender chicken, meat & fish', color: '#ff4757', bg: '#ffebee' },
    { id: 'colddrinks', label: 'Cold Drinks', icon: '🥤', desc: 'Chilled sodas & beverages', color: '#0288d1', bg: '#e1f5fe' },
    { id: 'icecreams', label: 'IceCreams', icon: '🍦', desc: 'Delicious cones, cups & scoops', color: '#8e24aa', bg: '#f3e5f5' },
];

const Home = () => {
    useSEO('Home', 'Discover the best food and drinks in your city with MealMate.');
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);

    const [foods, setFoods] = useState([]);
    const [restaurants, setRestaurants] = useState([]);
    const [search, setSearch] = useState('');
    const [activeFilter, setActiveFilter] = useState('all');
    const [loading, setLoading] = useState(true);
    const [addingId, setAddingId] = useState(null);
    const [toastMessage, setToastMessage] = useState(null);

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

    // Quick Add to Cart
    const handleAddToCart = async (e, food) => {
        e.preventDefault();
        e.stopPropagation();
        if (!user) {
            navigate('/login');
            return;
        }
        try {
            setAddingId(food.id);
            await api.post('cart-items/', { food_item: food.id, quantity: 1 });
            setToastMessage(`Added "${food.name}" to cart! 🛒`);
            setTimeout(() => setToastMessage(null), 3000);
        } catch (err) {
            console.error("Error adding to cart", err);
            setToastMessage('Failed to add item to cart. Please try again.');
            setTimeout(() => setToastMessage(null), 3000);
        } finally {
            setAddingId(null);
        }
    };

    // Category counts
    const categoryCounts = {
        all: foods.length,
        recommended: foods.filter(isRecommended).length,
        veg: foods.filter(isVeg).length,
        nonveg: foods.filter(isNonVeg).length,
        colddrinks: foods.filter(isColdDrink).length,
        icecreams: foods.filter(isIceCream).length,
    };

    // Filter logic
    const filteredFoods = foods.filter(f => {
        const matchSearch = (f.name || '').toLowerCase().includes(search.toLowerCase()) ||
            (f.restaurant_name || '').toLowerCase().includes(search.toLowerCase()) ||
            (f.cuisine_type || '').toLowerCase().includes(search.toLowerCase()) ||
            (f.category_name || '').toLowerCase().includes(search.toLowerCase());

        if (!matchSearch) return false;

        if (activeFilter === 'veg') return isVeg(f);
        if (activeFilter === 'nonveg') return isNonVeg(f);
        if (activeFilter === 'colddrinks') return isColdDrink(f);
        if (activeFilter === 'icecreams') return isIceCream(f);
        if (activeFilter === 'recommended') return isRecommended(f);
        return true;
    });

    // Curated recommendations (top 4 for showcase when browsing All)
    const topRecommendedFoods = foods.filter(isRecommended).slice(0, 4);

    const handleCategoryClick = (catId) => {
        setActiveFilter(catId);
        const section = document.getElementById('foods-section');
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const getFilterHeading = () => {
        if (search) return `Search results for "${search}"`;
        switch (activeFilter) {
            case 'veg':
                return '🥦 Pure Vegetarian Selection';
            case 'nonveg':
                return '🍗 Non-Vegetarian Delicacies';
            case 'colddrinks':
                return '🥤 Chilled Cold Drinks & Beverages';
            case 'icecreams':
                return '🍦 IceCreams & Frozen Treats';
            case 'recommended':
                return "⭐ Chef's Recommendations For You";
            default:
                return '🔥 Popular Dishes';
        }
    };

    const renderFoodCard = (food, isRecommendationSpotlight = false) => {
        const badgeInfo = getItemBadge(food);
        const recommended = isRecommended(food);

        return (
            <Col md={4} lg={3} className="mb-4" key={`${isRecommendationSpotlight ? 'rec-' : ''}${food.id}`}>
                <Card className="premium-card h-100 hover-scale position-relative">
                    {/* Image Box */}
                    <div style={{ height: '190px', backgroundColor: '#f1f2f6', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', position: 'relative' }}>
                        {food.image ? (
                            <img
                                src={food.image}
                                alt={food.name}
                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    if (e.target.nextElementSibling) {
                                        e.target.nextElementSibling.style.display = 'inline';
                                    }
                                }}
                            />
                        ) : null}
                        <span style={{ fontSize: '3rem', display: food.image ? 'none' : 'inline' }}>
                            {badgeInfo.icon}
                        </span>

                        {/* Top-Right Recommended Badge */}
                        {recommended && (
                            <div style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 2 }}>
                                <Badge className="badge-recommended shadow-sm" style={{ fontSize: '0.7rem', padding: '5px 8px', borderRadius: '8px' }}>
                                    ⭐ Recommended
                                </Badge>
                            </div>
                        )}
                    </div>

                    <Card.Body className="d-flex flex-column p-3">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                            <Card.Title className="fw-bold mb-0 fs-6 text-truncate" title={food.name} style={{ maxWidth: '70%' }}>
                                {food.name}
                            </Card.Title>
                            <Badge className={`${badgeInfo.className}`} style={{ fontSize: '0.68rem', padding: '4px 8px', borderRadius: '6px' }}>
                                {badgeInfo.icon} {badgeInfo.label}
                            </Badge>
                        </div>

                        {food.cuisine_type && (
                            <div className="mb-2">
                                <small className="text-secondary fw-semibold" style={{ fontSize: '0.75rem' }}>
                                    🏷️ {food.cuisine_type}
                                </small>
                            </div>
                        )}

                        <Card.Text className="text-muted mb-3" style={{ fontSize: '0.8rem' }}>
                            🏪 {food.restaurant_name}
                            {food.restaurant_location && <><br />📍 <span className="text-truncate d-inline-block" style={{ maxWidth: '90%' }}>{food.restaurant_location}</span></>}
                        </Card.Text>

                        {/* Price and Actions */}
                        <div className="d-flex justify-content-between align-items-center mt-auto pt-2 border-top">
                            <div>
                                <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>Price</small>
                                <h5 className="mb-0 fw-bold" style={{ color: 'var(--primary)' }}>₹{food.price}</h5>
                            </div>
                            <div className="d-flex gap-2">
                                <Button
                                    variant="outline-secondary"
                                    size="sm"
                                    as={Link}
                                    to={`/food/${food.id}`}
                                    style={{ borderRadius: '8px', fontSize: '0.8rem', padding: '5px 10px' }}
                                >
                                    View
                                </Button>
                                <Button
                                    variant="primary"
                                    size="sm"
                                    disabled={addingId === food.id}
                                    onClick={(e) => handleAddToCart(e, food)}
                                    style={{
                                        backgroundColor: 'var(--primary)',
                                        borderColor: 'var(--primary)',
                                        borderRadius: '8px',
                                        fontSize: '0.8rem',
                                        padding: '5px 12px',
                                        fontWeight: '600'
                                    }}
                                >
                                    {addingId === food.id ? (
                                        <Spinner animation="border" size="sm" />
                                    ) : (
                                        '+ Add'
                                    )}
                                </Button>
                            </div>
                        </div>
                    </Card.Body>
                </Card>
            </Col>
        );
    };

    const renderRestaurantCard = (rest) => (
        <Col md={4} lg={3} className="mb-4" key={rest.id}>
            <Card className="premium-card h-100 hover-scale">
                <div style={{ height: '170px', backgroundColor: '#f1f2f6', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {rest.image ? (
                        <img
                            src={rest.image}
                            alt={rest.name}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(e) => {
                                e.target.style.display = 'none';
                                if (e.target.nextElementSibling) {
                                    e.target.nextElementSibling.style.display = 'inline';
                                }
                            }}
                        />
                    ) : null}
                    <span style={{ fontSize: '3rem', display: rest.image ? 'none' : 'inline' }}>🏪</span>
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
            {/* Toast Feedback */}
            {toastMessage && (
                <div className="toast-notification">
                    <Alert variant="success" className="mb-0 d-flex align-items-center justify-content-between p-3 rounded-4 border-0 shadow-lg" style={{ background: '#2f3542', color: '#fff' }}>
                        <span>{toastMessage}</span>
                        <Button variant="link" size="sm" className="text-white text-decoration-none p-0 ms-3" onClick={() => setToastMessage(null)}>✕</Button>
                    </Alert>
                </div>
            )}

            {/* Hero Section */}
            <div className="text-white text-center py-5 mb-4" style={{ background: 'linear-gradient(135deg, var(--primary) 0%, #ff7b8f 100%)' }}>
                <Container>
                    <h1 className="display-4 fw-bold mb-2">Craving Something Delicious?</h1>
                    <p className="lead mb-4 opacity-75">Discover Veg, Non-Veg, Cold Drinks, IceCreams & Chef's Recommendations</p>
                    
                    {/* Search Input */}
                    <Row className="justify-content-center mb-4">
                        <Col md={7}>
                            <div className="glassmorphism p-2 d-flex gap-2 rounded-pill" style={{ background: 'rgba(255,255,255,0.2)' }}>
                                <Form.Control
                                    type="search"
                                    placeholder="Search dishes, drinks, ice creams, or restaurants..."
                                    className="border-0 shadow-none rounded-pill"
                                    style={{ background: 'rgba(255,255,255,0.95)', color: '#333' }}
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                />
                                <Button style={{ backgroundColor: 'var(--secondary)', border: 'none', borderRadius: '50px', paddingLeft: '20px', paddingRight: '20px' }}>
                                    🔍
                                </Button>
                            </div>
                        </Col>
                    </Row>

                    {/* Quick Filter Pills */}
                    <div className="d-flex justify-content-center gap-2 flex-wrap">
                        {CATEGORIES_CONFIG.map(cat => (
                            <Button
                                key={cat.id}
                                size="sm"
                                onClick={() => handleCategoryClick(cat.id)}
                                className="category-pill"
                                style={{
                                    background: activeFilter === cat.id ? 'white' : 'rgba(255,255,255,0.2)',
                                    color: activeFilter === cat.id ? 'var(--primary)' : 'white',
                                    border: 'none',
                                    boxShadow: activeFilter === cat.id ? '0 4px 15px rgba(0,0,0,0.15)' : 'none',
                                }}
                            >
                                {cat.icon} {cat.label} ({categoryCounts[cat.id] || 0})
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
                        {/* Interactive Category Cards Grid */}
                        <div className="mb-5">
                            <div className="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h3 className="fw-bold mb-0">🍽️ Explore Categories</h3>
                                    <p className="text-muted small mb-0">Choose your favorite category to quickly filter delicious food</p>
                                </div>
                                {activeFilter !== 'all' && (
                                    <Button
                                        variant="outline-danger"
                                        size="sm"
                                        onClick={() => setActiveFilter('all')}
                                        style={{ borderRadius: '20px' }}
                                    >
                                        ✕ Clear Filter
                                    </Button>
                                )}
                            </div>

                            <Row className="g-3">
                                {CATEGORIES_CONFIG.map(cat => {
                                    const isActive = activeFilter === cat.id;
                                    const count = categoryCounts[cat.id] || 0;
                                    return (
                                        <Col xs={6} sm={4} md={2} key={cat.id}>
                                            <div
                                                className={`category-card h-100 ${isActive ? 'active' : ''}`}
                                                onClick={() => handleCategoryClick(cat.id)}
                                            >
                                                <div className="category-icon-circle" style={{ backgroundColor: cat.bg }}>
                                                    {cat.icon}
                                                </div>
                                                <h6 className="fw-bold mb-1" style={{ color: isActive ? 'var(--primary)' : 'var(--text)' }}>
                                                    {cat.label}
                                                </h6>
                                                <small className="text-muted d-block" style={{ fontSize: '0.72rem' }}>
                                                    {count} item{count === 1 ? '' : 's'}
                                                </small>
                                            </div>
                                        </Col>
                                    );
                                })}
                            </Row>
                        </div>

                        {/* Chef's Recommendations Spotlight (shown when viewing All and not searching) */}
                        {!search && activeFilter === 'all' && topRecommendedFoods.length > 0 && (
                            <div className="mb-5 p-4 rounded-4" style={{ background: 'linear-gradient(135deg, rgba(255, 165, 2, 0.08) 0%, rgba(255, 71, 87, 0.08) 100%)', border: '1px solid rgba(255, 165, 2, 0.2)' }}>
                                <div className="d-flex justify-content-between align-items-center mb-4">
                                    <div>
                                        <div className="d-flex align-items-center gap-2">
                                            <h3 className="fw-bold mb-0">⭐ Chef's Recommendations</h3>
                                            <Badge bg="warning" text="dark" style={{ fontSize: '0.75rem', fontWeight: 'bold' }}>TOP PICKS</Badge>
                                        </div>
                                        <p className="text-muted small mb-0">Handpicked customer favorites and signature dishes</p>
                                    </div>
                                    <Button
                                        variant="outline-warning"
                                        size="sm"
                                        className="fw-semibold text-dark"
                                        style={{ borderRadius: '20px', borderColor: '#ffa502' }}
                                        onClick={() => handleCategoryClick('recommended')}
                                    >
                                        View All Recommendations →
                                    </Button>
                                </div>
                                <Row>
                                    {topRecommendedFoods.map(food => renderFoodCard(food, true))}
                                </Row>
                            </div>
                        )}

                        {/* Restaurants Section (shown when on All) */}
                        {!search && activeFilter === 'all' && restaurants.length > 0 && (
                            <div className="mb-5">
                                <h3 className="fw-bold mb-3">🏪 Top Restaurants Near You</h3>
                                <Row>
                                    {restaurants.map(renderRestaurantCard)}
                                </Row>
                            </div>
                        )}

                        {/* Filtered Dishes Section */}
                        <div id="foods-section" className="mb-5">
                            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                                <div>
                                    <h3 className="fw-bold mb-0">{getFilterHeading()}</h3>
                                    <p className="text-muted small mb-0">
                                        Showing {filteredFoods.length} delicious item{filteredFoods.length === 1 ? '' : 's'}
                                    </p>
                                </div>
                                {activeFilter !== 'all' && (
                                    <Badge bg="secondary" className="p-2 fs-6" style={{ cursor: 'pointer' }} onClick={() => setActiveFilter('all')}>
                                        Filter: {CATEGORIES_CONFIG.find(c => c.id === activeFilter)?.label} ✕
                                    </Badge>
                                )}
                            </div>

                            <Row>
                                {filteredFoods.map(food => renderFoodCard(food))}
                                {filteredFoods.length === 0 && (
                                    <Col className="text-center py-5">
                                        <p style={{ fontSize: '4rem' }}>🔍</p>
                                        <h4 className="fw-bold">No food items found</h4>
                                        <p className="text-muted">Try changing your category or searching for another dish.</p>
                                        <Button variant="primary" onClick={() => { setActiveFilter('all'); setSearch(''); }} style={{ backgroundColor: 'var(--primary)', border: 'none' }}>
                                            View All Foods
                                        </Button>
                                    </Col>
                                )}
                            </Row>
                        </div>
                    </>
                )}
            </Container>
        </div>
    );
};

export default Home;

