import React, { useState, useContext } from 'react';
import { Form, Button, Container, Card } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        phone_number: ''
    });
    const [error, setError] = useState(null);
    const { register } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await register(formData);
            navigate('/login');
        } catch (err) {
            if (err.response && err.response.data) {
                const data = err.response.data;
                const errorMessages = [];
                for (const key in data) {
                    if (Array.isArray(data[key])) {
                        errorMessages.push(`${key}: ${data[key].join(' ')}`);
                    } else if (typeof data[key] === 'string') {
                        errorMessages.push(data[key]);
                    }
                }
                setError(errorMessages.length > 0 ? errorMessages.join(' | ') : 'Registration failed. Please check your details and try again.');
            } else {
                setError('Registration failed. Please check your details and try again.');
            }
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center mt-5 mb-5">
            <Card className="premium-card p-4 hover-scale" style={{ width: '500px' }}>
                <Card.Body>
                    <h2 className="text-center mb-4" style={{ color: 'var(--primary)', fontWeight: 'bold' }}>Create an Account</h2>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Username *</Form.Label>
                            <Form.Control type="text" name="username" placeholder="Choose a username" value={formData.username} onChange={handleChange} required />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Email address *</Form.Label>
                            <Form.Control type="email" name="email" placeholder="Enter email" value={formData.email} onChange={handleChange} required />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Password *</Form.Label>
                            <Form.Control type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
                        </Form.Group>
                        <div className="row">
                            <div className="col-md-6">
                                <Form.Group className="mb-3">
                                    <Form.Label>First Name</Form.Label>
                                    <Form.Control type="text" name="first_name" placeholder="First Name" value={formData.first_name} onChange={handleChange} />
                                </Form.Group>
                            </div>
                            <div className="col-md-6">
                                <Form.Group className="mb-3">
                                    <Form.Label>Last Name</Form.Label>
                                    <Form.Control type="text" name="last_name" placeholder="Last Name" value={formData.last_name} onChange={handleChange} />
                                </Form.Group>
                            </div>
                        </div>
                        <Form.Group className="mb-4">
                            <Form.Label>Phone Number</Form.Label>
                            <Form.Control type="text" name="phone_number" placeholder="Phone Number" value={formData.phone_number} onChange={handleChange} />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100" style={{ backgroundColor: 'var(--primary)', border: 'none' }}>
                            Register
                        </Button>
                    </Form>
                    <div className="text-center mt-3">
                        <small className="text-muted">Already have an account? <Link to="/login" style={{ color: 'var(--primary)' }}>Login here</Link></small>
                    </div>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default Register;
