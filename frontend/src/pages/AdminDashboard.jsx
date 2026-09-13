import React, { useState, useEffect, useContext } from 'react';
import { Container, Card, Table, Badge, Button, Tabs, Tab, Modal, Form, Row, Col, InputGroup, Alert, Spinner } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AdminDashboard = () => {
    const { user, loading } = useContext(AuthContext);
    const navigate = useNavigate();

    const [restaurants, setRestaurants] = useState([]);
    const [foods, setFoods] = useState([]);
    const [categories, setCategories] = useState([]);
    const [orders, setOrders] = useState([]);
    const [dataLoading, setDataLoading] = useState(true);

    const [activeTab, setActiveTab] = useState('foods');
    const [foodSearch, setFoodSearch] = useState('');
    const [foodCategoryFilter, setFoodCategoryFilter] = useState('All');

    // Notifications
    const [alertMessage, setAlertMessage] = useState(null);
    const [alertVariant, setAlertVariant] = useState('success');

    // Modals
    const [showRestModal, setShowRestModal] = useState(false);
    const [restFormData, setRestFormData] = useState(null);

    const [showFoodModal, setShowFoodModal] = useState(false);
    const [foodFormData, setFoodFormData] = useState(null);

    const [quickPriceModal, setQuickPriceModal] = useState({ show: false, item: null, newPrice: '' });

    useEffect(() => {
        if (loading) return;
        if (!user || user.role !== 'Admin') {
            navigate('/');
            return;
        }
        fetchAllData();
    }, [user, loading, navigate]);

    const showNotification = (msg, variant = 'success') => {
        setAlertMessage(msg);
        setAlertVariant(variant);
        setTimeout(() => setAlertMessage(null), 3500);
    };

    const fetchAllData = async () => {
        setDataLoading(true);
        try {
            const [restRes, foodRes, catRes, orderRes] = await Promise.all([
                api.get('restaurants/'),
                api.get('foods/'),
                api.get('categories/'),
                api.get('orders/')
            ]);
            setRestaurants(Array.isArray(restRes.data) ? restRes.data : []);
            setFoods(Array.isArray(foodRes.data) ? foodRes.data : []);
            setCategories(Array.isArray(catRes.data) ? catRes.data : []);
            setOrders(Array.isArray(orderRes.data) ? orderRes.data : []);
        } catch (err) {
            console.error("Error fetching admin data", err);
            showNotification("Failed to load dashboard data.", "danger");
        } finally {
            setDataLoading(false);
        }
    };

    // ==========================================
    // FOOD ITEM HANDLERS (ADD / EDIT / DELETE / PRICE)
    // ==========================================
    const handleFoodModalOpen = (food = null) => {
        if (food) {
            setFoodFormData({
                id: food.id,
                name: food.name,
                description: food.description || '',
                price: food.price,
                veg_nonveg: food.veg_nonveg || 'Veg',
                cuisine_type: food.cuisine_type || '',
                image: food.image || '',
                is_available: food.is_available !== undefined ? food.is_available : true,
                restaurant: food.restaurant,
                category: food.category
            });
        } else {
            setFoodFormData({
                name: '',
                description: '',
                price: '',
                veg_nonveg: 'Veg',
                cuisine_type: 'Indian',
                image: '',
                is_available: true,
                restaurant: restaurants.length > 0 ? restaurants[0].id : '',
                category: categories.length > 0 ? categories[0].id : ''
            });
        }
        setShowFoodModal(true);
    };

    const handleFoodModalClose = () => {
        setShowFoodModal(false);
        setFoodFormData(null);
    };

    const handleFoodChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFoodFormData({
            ...foodFormData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleFoodSubmit = async (e) => {
        e.preventDefault();
        try {
            if (foodFormData.id) {
                await api.put(`foods/${foodFormData.id}/`, foodFormData);
                showNotification(`Food item "${foodFormData.name}" updated successfully!`);
            } else {
                await api.post('foods/', foodFormData);
                showNotification(`New food item "${foodFormData.name}" created!`);
            }
            handleFoodModalClose();
            const foodRes = await api.get('foods/');
            setFoods(foodRes.data);
        } catch (err) {
            console.error("Error saving food item", err);
            showNotification("Error saving food item. Please check the values.", "danger");
        }
    };

    const handleFoodDelete = async (id, name) => {
        if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
            try {
                await api.delete(`foods/${id}/`);
                showNotification(`"${name}" deleted successfully.`);
                setFoods(foods.filter(f => f.id !== id));
            } catch (err) {
                console.error("Error deleting food item", err);
                showNotification("Failed to delete food item.", "danger");
            }
        }
    };

    const handleToggleAvailability = async (food) => {
        try {
            const updated = !food.is_available;
            await api.patch(`foods/${food.id}/`, { is_available: updated });
            setFoods(foods.map(f => f.id === food.id ? { ...f, is_available: updated } : f));
            showNotification(`Updated status of "${food.name}" to ${updated ? 'Available' : 'Unavailable'}.`);
        } catch (err) {
            console.error("Error toggling availability", err);
            showNotification("Failed to update availability.", "danger");
        }
    };

    const handleQuickPriceSave = async () => {
        if (!quickPriceModal.item || !quickPriceModal.newPrice) return;
        try {
            const newPrice = parseFloat(quickPriceModal.newPrice);
            await api.patch(`foods/${quickPriceModal.item.id}/`, { price: newPrice });
            setFoods(foods.map(f => f.id === quickPriceModal.item.id ? { ...f, price: newPrice } : f));
            showNotification(`Price for "${quickPriceModal.item.name}" updated to ₹${newPrice}!`);
            setQuickPriceModal({ show: false, item: null, newPrice: '' });
        } catch (err) {
            console.error("Error updating price", err);
            showNotification("Failed to update price.", "danger");
        }
    };

    // ==========================================
    // ORDER MANAGEMENT HANDLERS
    // ==========================================
    const handleOrderStatusChange = async (orderId, newStatus) => {
        try {
            await api.patch(`orders/${orderId}/`, { status: newStatus });
            setOrders(orders.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
            showNotification(`Order #${orderId} status changed to "${newStatus}".`);
        } catch (err) {
            console.error("Error updating order status", err);
            showNotification("Failed to update order status.", "danger");
        }
    };

    // ==========================================
    // RESTAURANT HANDLERS
    // ==========================================
    const handleRestModalOpen = (rest = null) => {
        if (rest) {
            setRestFormData(rest);
        } else {
            setRestFormData({ name: '', description: '', location: '', veg_nonveg: 'Both', image: '', status: true });
        }
        setShowRestModal(true);
    };

    const handleRestModalClose = () => {
        setShowRestModal(false);
        setRestFormData(null);
    };

    const handleRestChange = (e) => {
        const { name, value, type, checked } = e.target;
        setRestFormData({ ...restFormData, [name]: type === 'checkbox' ? checked : value });
    };

    const handleRestSubmit = async (e) => {
        e.preventDefault();
        try {
            if (restFormData.id) {
                await api.put(`restaurants/${restFormData.id}/`, restFormData);
                showNotification(`Restaurant "${restFormData.name}" updated!`);
            } else {
                await api.post('restaurants/', restFormData);
                showNotification(`Restaurant "${restFormData.name}" created!`);
            }
            handleRestModalClose();
            const restRes = await api.get('restaurants/');
            setRestaurants(restRes.data);
        } catch (err) {
            console.error("Error saving restaurant", err);
            showNotification("Error saving restaurant.", "danger");
        }
    };

    const handleRestDelete = async (id, name) => {
        if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
            try {
                await api.delete(`restaurants/${id}/`);
                showNotification(`Restaurant "${name}" deleted.`);
                setRestaurants(restaurants.filter(r => r.id !== id));
            } catch (err) {
                console.error("Error deleting restaurant", err);
                showNotification("Failed to delete restaurant.", "danger");
            }
        }
    };

    if (loading || dataLoading) {
        return (
            <Container className="text-center py-5">
                <Spinner animation="border" variant="danger" />
                <p className="mt-3 text-muted">Loading Admin Portal...</p>
            </Container>
        );
    }

    if (!user || user.role !== 'Admin') return null;

    // Filter food items
    const filteredFoods = foods.filter(food => {
        const matchesSearch = food.name.toLowerCase().includes(foodSearch.toLowerCase()) ||
            (food.cuisine_type && food.cuisine_type.toLowerCase().includes(foodSearch.toLowerCase()));
        
        let matchesCategory = true;
        if (foodCategoryFilter !== 'All') {
            const catObj = categories.find(c => c.id === food.category);
            const catName = catObj ? catObj.name : '';
            matchesCategory = catName.toLowerCase() === foodCategoryFilter.toLowerCase() ||
                              food.veg_nonveg.toLowerCase() === foodCategoryFilter.toLowerCase();
        }
        return matchesSearch && matchesCategory;
    });

    const totalRevenue = orders.reduce((sum, o) => sum + Number(o.total_amount || 0), 0);

    return (
        <Container fluid className="py-4 px-md-5">
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold mb-1">
                        <span className="text-danger">⚙️ Admin</span> Management Portal
                    </h2>
                    <p className="text-muted mb-0">Control food items, update prices, manage restaurants, and track orders</p>
                </div>
                <div className="d-flex gap-2">
                    <Button variant="outline-secondary" size="sm" onClick={fetchAllData}>
                        🔄 Refresh Data
                    </Button>
                </div>
            </div>

            {/* Notification Alert */}
            {alertMessage && (
                <Alert variant={alertVariant} dismissible onClose={() => setAlertMessage(null)} className="shadow-sm">
                    {alertMessage}
                </Alert>
            )}

            {/* Top KPI Metric Cards */}
            <Row className="g-3 mb-4">
                <Col md={3} sm={6}>
                    <Card className="border-0 shadow-sm p-3 h-100" style={{ borderRadius: '14px', borderLeft: '5px solid #ff4757' }}>
                        <div className="d-flex justify-content-between align-items-center">
                            <div>
                                <span className="text-muted small text-uppercase fw-bold">Food Items</span>
                                <h3 className="fw-bold mb-0 mt-1">{foods.length}</h3>
                                <small className="text-success">{foods.filter(f => f.is_available).length} available</small>
                            </div>
                            <div style={{ fontSize: '2.2rem' }}>🍔</div>
                        </div>
                    </Card>
                </Col>

                <Col md={3} sm={6}>
                    <Card className="border-0 shadow-sm p-3 h-100" style={{ borderRadius: '14px', borderLeft: '5px solid #2ed573' }}>
                        <div className="d-flex justify-content-between align-items-center">
                            <div>
                                <span className="text-muted small text-uppercase fw-bold">Total Orders</span>
                                <h3 className="fw-bold mb-0 mt-1">{orders.length}</h3>
                                <small className="text-primary">{orders.filter(o => o.status !== 'Delivered' && o.status !== 'Cancelled').length} active</small>
                            </div>
                            <div style={{ fontSize: '2.2rem' }}>📦</div>
                        </div>
                    </Card>
                </Col>

                <Col md={3} sm={6}>
                    <Card className="border-0 shadow-sm p-3 h-100" style={{ borderRadius: '14px', borderLeft: '5px solid #1e90ff' }}>
                        <div className="d-flex justify-content-between align-items-center">
                            <div>
                                <span className="text-muted small text-uppercase fw-bold">Gross Revenue</span>
                                <h3 className="fw-bold mb-0 mt-1" style={{ color: '#1e90ff' }}>₹{totalRevenue}</h3>
                                <small className="text-muted">From {orders.length} orders</small>
                            </div>
                            <div style={{ fontSize: '2.2rem' }}>💰</div>
                        </div>
                    </Card>
                </Col>

                <Col md={3} sm={6}>
                    <Card className="border-0 shadow-sm p-3 h-100" style={{ borderRadius: '14px', borderLeft: '5px solid #ffa502' }}>
                        <div className="d-flex justify-content-between align-items-center">
                            <div>
                                <span className="text-muted small text-uppercase fw-bold">Restaurants</span>
                                <h3 className="fw-bold mb-0 mt-1">{restaurants.length}</h3>
                                <small className="text-muted">Partners onboarded</small>
                            </div>
                            <div style={{ fontSize: '2.2rem' }}>🏨</div>
                        </div>
                    </Card>
                </Col>
            </Row>

            {/* Main Tabs */}
            <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="mb-4 custom-tabs border-bottom"
            >
                {/* TAB 1: FOOD ITEMS & PRICING */}
                <Tab eventKey="foods" title="🍔 Food Items & Pricing">
                    <Card className="border-0 shadow-sm p-4" style={{ borderRadius: '16px' }}>
                        {/* Search & Filter Bar */}
                        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
                            <div className="d-flex gap-2 flex-grow-1" style={{ maxWidth: '600px' }}>
                                <InputGroup>
                                    <InputGroup.Text style={{ backgroundColor: '#f8f9fa' }}>🔍</InputGroup.Text>
                                    <Form.Control
                                        type="text"
                                        placeholder="Search by food name or cuisine..."
                                        value={foodSearch}
                                        onChange={(e) => setFoodSearch(e.target.value)}
                                    />
                                    {foodSearch && (
                                        <Button variant="outline-secondary" onClick={() => setFoodSearch('')}>✕</Button>
                                    )}
                                </InputGroup>

                                <Form.Select
                                    value={foodCategoryFilter}
                                    onChange={(e) => setFoodCategoryFilter(e.target.value)}
                                    style={{ maxWidth: '180px' }}
                                >
                                    <option value="All">All Categories</option>
                                    <option value="Veg">Pure Veg</option>
                                    <option value="Non-Veg">Non-Veg</option>
                                    <option value="Cold Drinks">Cold Drinks</option>
                                    <option value="IceCreams">Ice Creams</option>
                                </Form.Select>
                            </div>

                            <Button 
                                variant="primary" 
                                className="fw-bold px-3 shadow-sm"
                                style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)', borderRadius: '10px' }}
                                onClick={() => handleFoodModalOpen()}
                            >
                                + Add New Food Item
                            </Button>
                        </div>

                        {/* Food Items Table */}
                        <Table responsive hover align="middle" className="border-top">
                            <thead className="table-light">
                                <tr>
                                    <th>Item</th>
                                    <th>Restaurant</th>
                                    <th>Category & Type</th>
                                    <th>Price (₹)</th>
                                    <th>Availability</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredFoods.length === 0 ? (
                                    <tr>
                                        <td colSpan="6" className="text-center py-5 text-muted">
                                            No food items found matching your criteria.
                                        </td>
                                    </tr>
                                ) : (
                                    filteredFoods.map(food => {
                                        const restName = restaurants.find(r => r.id === food.restaurant)?.name || 'N/A';
                                        const catName = categories.find(c => c.id === food.category)?.name || 'General';

                                        return (
                                            <tr key={food.id}>
                                                <td>
                                                    <div className="d-flex align-items-center gap-3">
                                                        <div style={{ width: '52px', height: '52px', borderRadius: '10px', overflow: 'hidden', backgroundColor: '#f1f2f6', flexShrink: 0 }}>
                                                            <img
                                                                src={food.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'}
                                                                alt={food.name}
                                                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                                onError={(e) => {
                                                                    e.target.onerror = null;
                                                                    e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500';
                                                                }}
                                                            />
                                                        </div>
                                                        <div>
                                                            <div className="fw-bold text-dark">{food.name}</div>
                                                            <small className="text-muted">{food.cuisine_type || 'Special'}</small>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <span className="text-muted small">{restName}</span>
                                                </td>
                                                <td>
                                                    <Badge bg={food.veg_nonveg === 'Veg' ? 'success' : 'danger'} className="me-2">
                                                        {food.veg_nonveg}
                                                    </Badge>
                                                    <Badge bg="secondary" className="text-capitalize">
                                                        {catName}
                                                    </Badge>
                                                </td>
                                                <td>
                                                    <div className="d-flex align-items-center gap-2">
                                                        <span className="fw-bold fs-6 text-primary">₹{food.price}</span>
                                                        <Button
                                                            variant="link"
                                                            size="sm"
                                                            className="p-0 text-muted"
                                                            title="Quick update price"
                                                            onClick={() => setQuickPriceModal({ show: true, item: food, newPrice: food.price })}
                                                        >
                                                            ✏️
                                                        </Button>
                                                    </div>
                                                </td>
                                                <td>
                                                    <Button
                                                        variant={food.is_available ? "outline-success" : "outline-secondary"}
                                                        size="sm"
                                                        style={{ borderRadius: '20px', fontSize: '0.75rem' }}
                                                        onClick={() => handleToggleAvailability(food)}
                                                    >
                                                        {food.is_available ? '● Available' : '○ Unavailable'}
                                                    </Button>
                                                </td>
                                                <td className="text-end">
                                                    <Button
                                                        variant="outline-primary"
                                                        size="sm"
                                                        className="me-2"
                                                        onClick={() => handleFoodModalOpen(food)}
                                                    >
                                                        Edit
                                                    </Button>
                                                    <Button
                                                        variant="outline-danger"
                                                        size="sm"
                                                        onClick={() => handleFoodDelete(food.id, food.name)}
                                                    >
                                                        Delete
                                                    </Button>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </Table>
                    </Card>
                </Tab>

                {/* TAB 2: ORDER MANAGEMENT */}
                <Tab eventKey="orders" title="📋 Customer Orders">
                    <Card className="border-0 shadow-sm p-4" style={{ borderRadius: '16px' }}>
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <h4 className="fw-bold mb-0">All Customer Orders ({orders.length})</h4>
                        </div>

                        <Table responsive hover align="middle">
                            <thead className="table-light">
                                <tr>
                                    <th>Order #</th>
                                    <th>Date</th>
                                    <th>Items Ordered</th>
                                    <th>Total Amount</th>
                                    <th>Update Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {orders.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" className="text-center py-5 text-muted">
                                            No customer orders recorded yet.
                                        </td>
                                    </tr>
                                ) : (
                                    orders.map(order => (
                                        <tr key={order.id}>
                                            <td className="fw-bold text-dark">#{order.id}</td>
                                            <td>
                                                <small className="text-muted">
                                                    {new Date(order.created_at).toLocaleDateString()} {new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </small>
                                            </td>
                                            <td>
                                                {order.items && order.items.length > 0 ? (
                                                    order.items.map((i, idx) => (
                                                        <div key={idx} className="small">
                                                            <span className="fw-bold">{i.quantity}x</span> {i.food_item_details?.name || 'Food item'}
                                                        </div>
                                                    ))
                                                ) : (
                                                    <span className="text-muted small">Meal items</span>
                                                )}
                                            </td>
                                            <td className="fw-bold text-primary">₹{order.total_amount}</td>
                                            <td style={{ minWidth: '180px' }}>
                                                <Form.Select
                                                    size="sm"
                                                    value={order.status}
                                                    onChange={(e) => handleOrderStatusChange(order.id, e.target.value)}
                                                    style={{
                                                        fontWeight: '600',
                                                        borderColor: order.status === 'Delivered' ? '#2ed573' : order.status === 'Cancelled' ? '#ff4757' : '#ffa502'
                                                    }}
                                                >
                                                    <option value="Pending">🟡 Pending</option>
                                                    <option value="Confirmed">🟠 Confirmed</option>
                                                    <option value="Preparing">🔵 Preparing</option>
                                                    <option value="Out for Delivery">🟣 Out for Delivery</option>
                                                    <option value="Delivered">🟢 Delivered</option>
                                                    <option value="Cancelled">🔴 Cancelled</option>
                                                </Form.Select>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </Table>
                    </Card>
                </Tab>

                {/* TAB 3: RESTAURANTS MANAGEMENT */}
                <Tab eventKey="restaurants" title="🏨 Restaurants">
                    <Card className="border-0 shadow-sm p-4" style={{ borderRadius: '16px' }}>
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <h4 className="fw-bold m-0">Partner Restaurants ({restaurants.length})</h4>
                            <Button variant="primary" onClick={() => handleRestModalOpen()}>+ Add Restaurant</Button>
                        </div>
                        <Table responsive hover align="middle">
                            <thead className="table-light">
                                <tr>
                                    <th>Restaurant</th>
                                    <th>Location</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {restaurants.map(rest => (
                                    <tr key={rest.id}>
                                        <td>
                                            <div className="d-flex align-items-center gap-3">
                                                <div style={{ width: '48px', height: '48px', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#f1f2f6' }}>
                                                    <img
                                                        src={rest.image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500'}
                                                        alt={rest.name}
                                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                        onError={(e) => {
                                                            e.target.onerror = null;
                                                            e.target.src = 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500';
                                                        }}
                                                    />
                                                </div>
                                                <div>
                                                    <span className="fw-bold">{rest.name}</span>
                                                    <div className="text-muted small">{rest.description?.substring(0, 40)}...</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>{rest.location}</td>
                                        <td>
                                            <Badge bg="secondary">{rest.veg_nonveg}</Badge>
                                        </td>
                                        <td>
                                            <Badge bg={rest.status ? 'success' : 'secondary'}>
                                                {rest.status ? 'Active' : 'Inactive'}
                                            </Badge>
                                        </td>
                                        <td className="text-end">
                                            <Button variant="outline-primary" size="sm" className="me-2" onClick={() => handleRestModalOpen(rest)}>Edit</Button>
                                            <Button variant="outline-danger" size="sm" onClick={() => handleRestDelete(rest.id, rest.name)}>Delete</Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </Card>
                </Tab>
            </Tabs>

            {/* QUICK PRICE UPDATE MODAL */}
            <Modal show={quickPriceModal.show} onHide={() => setQuickPriceModal({ show: false, item: null, newPrice: '' })} centered size="sm">
                <Modal.Header closeButton>
                    <Modal.Title className="fs-6 fw-bold">Update Price</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p className="mb-2 small text-muted">Modify price for <strong>{quickPriceModal.item?.name}</strong>:</p>
                    <InputGroup className="mb-3">
                        <InputGroup.Text>₹</InputGroup.Text>
                        <Form.Control
                            type="number"
                            step="0.01"
                            value={quickPriceModal.newPrice}
                            onChange={(e) => setQuickPriceModal({ ...quickPriceModal, newPrice: e.target.value })}
                            autoFocus
                        />
                    </InputGroup>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" size="sm" onClick={() => setQuickPriceModal({ show: false, item: null, newPrice: '' })}>
                        Cancel
                    </Button>
                    <Button variant="primary" size="sm" onClick={handleQuickPriceSave}>
                        Save New Price
                    </Button>
                </Modal.Footer>
            </Modal>

            {/* FOOD ADD / EDIT MODAL */}
            <Modal show={showFoodModal} onHide={handleFoodModalClose} size="lg" centered>
                <Modal.Header closeButton>
                    <Modal.Title className="fw-bold">{foodFormData?.id ? '✏️ Modify Food Item' : '➕ Add New Food Item'}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {foodFormData && (
                        <Form onSubmit={handleFoodSubmit}>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Item Name *</Form.Label>
                                        <Form.Control required type="text" name="name" value={foodFormData.name} onChange={handleFoodChange} placeholder="e.g. Paneer Butter Masala" />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Price (₹) *</Form.Label>
                                        <Form.Control required type="number" step="0.01" name="price" value={foodFormData.price} onChange={handleFoodChange} placeholder="e.g. 240" />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Restaurant *</Form.Label>
                                        <Form.Select required name="restaurant" value={foodFormData.restaurant || ''} onChange={handleFoodChange}>
                                            <option value="">Select Restaurant...</option>
                                            {restaurants.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Category *</Form.Label>
                                        <Form.Select required name="category" value={foodFormData.category || ''} onChange={handleFoodChange}>
                                            <option value="">Select Category...</option>
                                            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Food Type</Form.Label>
                                        <Form.Select name="veg_nonveg" value={foodFormData.veg_nonveg} onChange={handleFoodChange}>
                                            <option value="Veg">Veg</option>
                                            <option value="Non-Veg">Non-Veg</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold small">Cuisine / Tag</Form.Label>
                                        <Form.Control type="text" name="cuisine_type" value={foodFormData.cuisine_type || ''} onChange={handleFoodChange} placeholder="e.g. North Indian / Beverage" />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Image URL</Form.Label>
                                <Form.Control type="url" name="image" value={foodFormData.image || ''} onChange={handleFoodChange} placeholder="https://example.com/image.jpg" />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Description</Form.Label>
                                <Form.Control as="textarea" rows={2} name="description" value={foodFormData.description || ''} onChange={handleFoodChange} placeholder="Short appetizing description..." />
                            </Form.Group>

                            <Form.Group className="mb-4" controlId="foodStatus">
                                <Form.Check type="checkbox" label="Item Available for Ordering" name="is_available" checked={foodFormData.is_available} onChange={handleFoodChange} />
                            </Form.Group>

                            <div className="d-flex justify-content-end gap-2">
                                <Button variant="secondary" onClick={handleFoodModalClose}>Cancel</Button>
                                <Button variant="primary" type="submit" style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)' }}>
                                    {foodFormData.id ? 'Save Changes' : 'Create Food Item'}
                                </Button>
                            </div>
                        </Form>
                    )}
                </Modal.Body>
            </Modal>

            {/* RESTAURANT MODAL */}
            <Modal show={showRestModal} onHide={handleRestModalClose} centered>
                <Modal.Header closeButton>
                    <Modal.Title className="fw-bold">{restFormData?.id ? '✏️ Edit Restaurant' : '➕ Add Restaurant'}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {restFormData && (
                        <Form onSubmit={handleRestSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Restaurant Name *</Form.Label>
                                <Form.Control required type="text" name="name" value={restFormData.name} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Description</Form.Label>
                                <Form.Control as="textarea" rows={2} name="description" value={restFormData.description} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Location</Form.Label>
                                <Form.Control type="text" name="location" value={restFormData.location} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Food Style</Form.Label>
                                <Form.Select name="veg_nonveg" value={restFormData.veg_nonveg} onChange={handleRestChange}>
                                    <option value="Both">Both (Veg & Non-Veg)</option>
                                    <option value="Veg">Pure Vegetarian</option>
                                    <option value="Non-Veg">Non-Vegetarian</option>
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold small">Image URL</Form.Label>
                                <Form.Control type="url" name="image" value={restFormData.image || ''} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3" controlId="restStatus">
                                <Form.Check type="checkbox" label="Restaurant Active" name="status" checked={restFormData.status} onChange={handleRestChange} />
                            </Form.Group>
                            <div className="d-flex justify-content-end gap-2">
                                <Button variant="secondary" onClick={handleRestModalClose}>Cancel</Button>
                                <Button variant="primary" type="submit" style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)' }}>
                                    Save Restaurant
                                </Button>
                            </div>
                        </Form>
                    )}
                </Modal.Body>
            </Modal>
        </Container>
    );
};

export default AdminDashboard;
