import React, { useState, useEffect, useContext } from 'react';
import { Container, Card, Table, Badge, Button, Tabs, Tab, Modal, Form } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AdminDashboard = () => {
    const { user, loading } = useContext(AuthContext);
    const navigate = useNavigate();

    const [restaurants, setRestaurants] = useState([]);
    const [foods, setFoods] = useState([]);
    const [categories, setCategories] = useState([]);

    const [activeTab, setActiveTab] = useState('restaurants');

    const [showRestModal, setShowRestModal] = useState(false);
    const [restFormData, setRestFormData] = useState(null);

    const [showFoodModal, setShowFoodModal] = useState(false);
    const [foodFormData, setFoodFormData] = useState(null);

    useEffect(() => {
        if (loading) return; // Wait for auth to load
        if (!user || user.role !== 'Admin') {
            navigate('/');
            return;
        }
        fetchData();
    }, [user, loading, navigate]);


    const fetchData = async () => {
        try {
            const [restRes, foodRes, catRes] = await Promise.all([
                api.get('restaurants/'),
                api.get('foods/'),
                api.get('categories/')
            ]);
            setRestaurants(restRes.data);
            setFoods(foodRes.data);
            setCategories(catRes.data);
        } catch (err) {
            console.error("Error fetching admin data", err);
        }
    };

    // --- RESTAURANT HANDLERS ---
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
            } else {
                await api.post('restaurants/', restFormData);
            }
            fetchData();
            handleRestModalClose();
        } catch (err) {
            console.error("Error saving restaurant", err);
        }
    };

    const handleRestDelete = async (id) => {
        if(window.confirm("Are you sure you want to delete this restaurant?")) {
            try {
                await api.delete(`restaurants/${id}/`);
                fetchData();
            } catch (err) {
                console.error("Error deleting restaurant", err);
            }
        }
    };

    // --- FOOD HANDLERS ---
    const handleFoodModalOpen = (food = null) => {
        if (food) {
            setFoodFormData({
                ...food,
                restaurant: food.restaurant,
                category: food.category
            });
        } else {
            setFoodFormData({ 
                name: '', description: '', price: '', veg_nonveg: 'Veg', cuisine_type: '', 
                image: '', is_available: true, restaurant: '', category: '' 
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
        setFoodFormData({ ...foodFormData, [name]: type === 'checkbox' ? checked : value });
    };

    const handleFoodSubmit = async (e) => {
        e.preventDefault();
        try {
            if (foodFormData.id) {
                await api.put(`foods/${foodFormData.id}/`, foodFormData);
            } else {
                await api.post('foods/', foodFormData);
            }
            fetchData();
            handleFoodModalClose();
        } catch (err) {
            console.error("Error saving food", err);
        }
    };

    const handleFoodDelete = async (id) => {
        if(window.confirm("Are you sure you want to delete this menu item?")) {
            try {
                await api.delete(`foods/${id}/`);
                fetchData();
            } catch (err) {
                console.error("Error deleting food", err);
            }
        }
    };

    if (loading) return <div className="text-center mt-5">Loading...</div>;
    if (!user || user.role !== 'Admin') return null;

    return (
        <Container fluid className="mt-5 px-5 pb-5">
            <h2 className="fw-bold mb-4">Admin Dashboard</h2>
            
            <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="mb-4 custom-tabs"
            >
                <Tab eventKey="restaurants" title="Manage Restaurants">
                    <Card className="premium-card p-4">
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <h4 className="fw-bold m-0">Restaurants</h4>
                            <Button variant="primary" onClick={() => handleRestModalOpen()}>+ Add Restaurant</Button>
                        </div>
                        <Table responsive hover>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Location</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {restaurants.map(rest => (
                                    <tr key={rest.id}>
                                        <td>{rest.id}</td>
                                        <td>{rest.name}</td>
                                        <td>{rest.location}</td>
                                        <td>{rest.veg_nonveg}</td>
                                        <td>
                                            <Badge bg={rest.status ? 'success' : 'secondary'}>
                                                {rest.status ? 'Active' : 'Inactive'}
                                            </Badge>
                                        </td>
                                        <td>
                                            <Button variant="outline-primary" size="sm" className="me-2" onClick={() => handleRestModalOpen(rest)}>Edit</Button>
                                            <Button variant="outline-danger" size="sm" onClick={() => handleRestDelete(rest.id)}>Delete</Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </Card>
                </Tab>
                <Tab eventKey="menu" title="Manage Menu">
                    <Card className="premium-card p-4">
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <h4 className="fw-bold m-0">Menu Items</h4>
                            <Button variant="primary" onClick={() => handleFoodModalOpen()}>+ Add Menu Item</Button>
                        </div>
                        <Table responsive hover>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Restaurant</th>
                                    <th>Price</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {foods.map(food => {
                                    const restName = restaurants.find(r => r.id === food.restaurant)?.name || 'Unknown';
                                    return (
                                    <tr key={food.id}>
                                        <td>{food.id}</td>
                                        <td>{food.name}</td>
                                        <td>{restName}</td>
                                        <td>₹{food.price}</td>
                                        <td>{food.veg_nonveg}</td>
                                        <td>
                                            <Badge bg={food.is_available ? 'success' : 'secondary'}>
                                                {food.is_available ? 'Available' : 'Unavailable'}
                                            </Badge>
                                        </td>
                                        <td>
                                            <Button variant="outline-primary" size="sm" className="me-2" onClick={() => handleFoodModalOpen(food)}>Edit</Button>
                                            <Button variant="outline-danger" size="sm" onClick={() => handleFoodDelete(food.id)}>Delete</Button>
                                        </td>
                                    </tr>
                                    );
                                })}
                            </tbody>
                        </Table>
                    </Card>
                </Tab>
            </Tabs>

            {/* RESTAURANT MODAL */}
            <Modal show={showRestModal} onHide={handleRestModalClose}>
                <Modal.Header closeButton>
                    <Modal.Title>{restFormData?.id ? 'Edit Restaurant' : 'Add Restaurant'}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {restFormData && (
                        <Form onSubmit={handleRestSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Name</Form.Label>
                                <Form.Control required type="text" name="name" value={restFormData.name} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Description</Form.Label>
                                <Form.Control as="textarea" name="description" value={restFormData.description} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Location</Form.Label>
                                <Form.Control type="text" name="location" value={restFormData.location} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Veg/Non-Veg</Form.Label>
                                <Form.Select name="veg_nonveg" value={restFormData.veg_nonveg} onChange={handleRestChange}>
                                    <option value="Both">Both</option>
                                    <option value="Veg">Pure Vegetarian</option>
                                    <option value="Non-Veg">Non-Vegetarian</option>
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Image URL</Form.Label>
                                <Form.Control type="url" name="image" value={restFormData.image || ''} onChange={handleRestChange} />
                            </Form.Group>
                            <Form.Group className="mb-3" controlId="restStatus">
                                <Form.Check type="checkbox" label="Active" name="status" checked={restFormData.status} onChange={handleRestChange} />
                            </Form.Group>
                            <Button variant="primary" type="submit" className="w-100">Save</Button>
                        </Form>
                    )}
                </Modal.Body>
            </Modal>

            {/* FOOD MODAL */}
            <Modal show={showFoodModal} onHide={handleFoodModalClose}>
                <Modal.Header closeButton>
                    <Modal.Title>{foodFormData?.id ? 'Edit Menu Item' : 'Add Menu Item'}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {foodFormData && (
                        <Form onSubmit={handleFoodSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Restaurant</Form.Label>
                                <Form.Select required name="restaurant" value={foodFormData.restaurant || ''} onChange={handleFoodChange}>
                                    <option value="">Select Restaurant...</option>
                                    {restaurants.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Category</Form.Label>
                                <Form.Select name="category" value={foodFormData.category || ''} onChange={handleFoodChange}>
                                    <option value="">Select Category...</option>
                                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Name</Form.Label>
                                <Form.Control required type="text" name="name" value={foodFormData.name} onChange={handleFoodChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Description</Form.Label>
                                <Form.Control as="textarea" name="description" value={foodFormData.description || ''} onChange={handleFoodChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Price</Form.Label>
                                <Form.Control required type="number" step="0.01" name="price" value={foodFormData.price} onChange={handleFoodChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Veg/Non-Veg</Form.Label>
                                <Form.Select name="veg_nonveg" value={foodFormData.veg_nonveg} onChange={handleFoodChange}>
                                    <option value="Veg">Veg</option>
                                    <option value="Non-Veg">Non-Veg</option>
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Cuisine Type</Form.Label>
                                <Form.Control type="text" name="cuisine_type" value={foodFormData.cuisine_type || ''} onChange={handleFoodChange} />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Image URL</Form.Label>
                                <Form.Control type="url" name="image" value={foodFormData.image || ''} onChange={handleFoodChange} />
                            </Form.Group>
                            <Form.Group className="mb-3" controlId="foodStatus">
                                <Form.Check type="checkbox" label="Available" name="is_available" checked={foodFormData.is_available} onChange={handleFoodChange} />
                            </Form.Group>
                            <Button variant="primary" type="submit" className="w-100">Save</Button>
                        </Form>
                    )}
                </Modal.Body>
            </Modal>
        </Container>
    );
};

export default AdminDashboard;
