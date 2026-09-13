import React, { useState, useContext } from 'react';
import { Form, Button, Container, Card, InputGroup, Row, Col } from 'react-bootstrap';
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
    const [showPass, setShowPass] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const { register, login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            await register(formData);
            // Auto-login after registration
            await login(formData.username, formData.password);
            navigate('/');
        } catch (err) {
            if (err.response && err.response.data) {
                const data = err.response.data;
                const msgs = [];
                for (const key in data) {
                    if (Array.isArray(data[key])) msgs.push(`${key}: ${data[key].join(' ')}`);
                    else if (typeof data[key] === 'string') msgs.push(data[key]);
                }
                setError(msgs.length > 0 ? msgs.join(' | ') : 'Registration failed. Please check your details.');
            } else {
                setError('Registration failed. Please check your details and try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #fff5f5 0%, #fff 60%, #f8f9fa 100%)', display: 'flex', alignItems: 'center' }}>
            <Container className="d-flex justify-content-center align-items-center py-5">
                <Card className="border-0 shadow-lg" style={{ width: '520px', borderRadius: '20px', overflow: 'hidden' }}>
                    <div style={{ height: '5px', background: 'linear-gradient(90deg, #ff4757, #ff6b81)' }} />
                    <Card.Body className="p-5">
                        <div className="text-center mb-4">
                            <div style={{ fontSize: '2.5rem' }}>🍔</div>
                            <h2 className="fw-bold mb-1" style={{ color: 'var(--primary)' }}>Create Account</h2>
                            <p className="text-muted small">Join MealMate and start ordering food online!</p>
                        </div>

                        {error && (
                            <div className="alert alert-danger d-flex align-items-center gap-2 py-2" style={{ borderRadius: '10px', fontSize: '0.9rem' }}>
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Username *</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>👤</InputGroup.Text>
                                    <Form.Control
                                        type="text" name="username" placeholder="Choose a username"
                                        value={formData.username} onChange={handleChange} required
                                        style={{ borderLeft: 'none', boxShadow: 'none' }}
                                    />
                                </InputGroup>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Email *</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>📧</InputGroup.Text>
                                    <Form.Control
                                        type="email" name="email" placeholder="Enter your email"
                                        value={formData.email} onChange={handleChange} required
                                        style={{ borderLeft: 'none', boxShadow: 'none' }}
                                    />
                                </InputGroup>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Password *</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>🔒</InputGroup.Text>
                                    <Form.Control
                                        type={showPass ? 'text' : 'password'} name="password" placeholder="Create a password"
                                        value={formData.password} onChange={handleChange} required
                                        style={{ borderLeft: 'none', borderRight: 'none', boxShadow: 'none' }}
                                    />
                                    <InputGroup.Text onClick={() => setShowPass(!showPass)} style={{ cursor: 'pointer', background: '#f8f9fa', border: '1px solid #e9ecef', borderLeft: 'none' }}>
                                        {showPass ? '🙈' : '👁️'}
                                    </InputGroup.Text>
                                </InputGroup>
                            </Form.Group>

                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>First Name</Form.Label>
                                        <Form.Control
                                            type="text" name="first_name" placeholder="First name"
                                            value={formData.first_name} onChange={handleChange}
                                            style={{ boxShadow: 'none' }}
                                        />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Last Name</Form.Label>
                                        <Form.Control
                                            type="text" name="last_name" placeholder="Last name"
                                            value={formData.last_name} onChange={handleChange}
                                            style={{ boxShadow: 'none' }}
                                        />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Form.Group className="mb-4">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Phone Number</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>📱</InputGroup.Text>
                                    <Form.Control
                                        type="text" name="phone_number" placeholder="Enter phone number"
                                        value={formData.phone_number} onChange={handleChange}
                                        style={{ borderLeft: 'none', boxShadow: 'none' }}
                                    />
                                </InputGroup>
                            </Form.Group>

                            <Button
                                variant="primary" type="submit"
                                className="w-100 fw-bold py-2"
                                disabled={loading}
                                style={{ backgroundColor: 'var(--primary)', border: 'none', borderRadius: '10px', fontSize: '1rem' }}
                            >
                                {loading ? '⏳ Creating account...' : '✅ Create Account'}
                            </Button>
                        </Form>

                        <div className="text-center mt-3">
                            <small className="text-muted">
                                Already have an account?{' '}
                                <Link to="/login" style={{ color: 'var(--primary)', fontWeight: '600', textDecoration: 'none' }}>
                                    Sign in here
                                </Link>
                            </small>
                        </div>
                    </Card.Body>
                </Card>
            </Container>
        </div>
    );
};

export default Register;
