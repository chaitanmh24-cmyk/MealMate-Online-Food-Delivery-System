import React, { useState, useContext } from 'react';
import { Form, Button, Container, Card, InputGroup } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPass, setShowPass] = useState(false);
    const [error, setError] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            const userData = await login(username, password);
            if (userData && userData.role === 'Admin') {
                navigate('/admin');
            } else {
                navigate('/');
            }
        } catch (err) {
            setError('Invalid username or password. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #fff5f5 0%, #fff 60%, #f8f9fa 100%)', display: 'flex', alignItems: 'center' }}>
            <Container className="d-flex justify-content-center align-items-center py-5">
                <Card className="border-0 shadow-lg" style={{ width: '420px', borderRadius: '20px', overflow: 'hidden' }}>
                    <div style={{ height: '5px', background: 'linear-gradient(90deg, #ff4757, #ff6b81)' }} />
                    <Card.Body className="p-5">
                        <div className="text-center mb-4">
                            <div style={{ fontSize: '2.5rem' }}>🍔</div>
                            <h2 className="fw-bold mb-1" style={{ color: 'var(--primary)' }}>MealMate</h2>
                            <p className="text-muted small">Welcome back! Sign in to continue</p>
                        </div>

                        {error && (
                            <div className="alert alert-danger d-flex align-items-center gap-2 py-2" style={{ borderRadius: '10px', fontSize: '0.9rem' }}>
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Username</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>👤</InputGroup.Text>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter your username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                        style={{ borderLeft: 'none', boxShadow: 'none' }}
                                    />
                                </InputGroup>
                            </Form.Group>

                            <Form.Group className="mb-4">
                                <Form.Label className="fw-semibold text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Password</Form.Label>
                                <InputGroup>
                                    <InputGroup.Text style={{ background: '#f8f9fa', border: '1px solid #e9ecef', borderRight: 'none' }}>🔒</InputGroup.Text>
                                    <Form.Control
                                        type={showPass ? 'text' : 'password'}
                                        placeholder="Enter your password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        style={{ borderLeft: 'none', borderRight: 'none', boxShadow: 'none' }}
                                    />
                                    <InputGroup.Text
                                        onClick={() => setShowPass(!showPass)}
                                        style={{ cursor: 'pointer', background: '#f8f9fa', border: '1px solid #e9ecef', borderLeft: 'none' }}
                                    >
                                        {showPass ? '🙈' : '👁️'}
                                    </InputGroup.Text>
                                </InputGroup>
                            </Form.Group>

                            <Button
                                variant="primary" type="submit"
                                className="w-100 fw-bold py-2"
                                disabled={submitting}
                                style={{ backgroundColor: 'var(--primary)', border: 'none', borderRadius: '10px', fontSize: '1rem' }}
                            >
                                {submitting ? '⏳ Signing in...' : '🚀 Sign In'}
                            </Button>
                        </Form>

                        <div className="mt-4 p-3 rounded" style={{ background: '#f8f9fa', fontSize: '0.8rem' }}>
                            <p className="fw-bold text-muted mb-1">Demo Accounts:</p>
                            <p className="mb-0 text-muted">👤 Customer: <code>customer</code> / <code>customer123</code></p>
                            <p className="mb-0 text-muted">🔑 Admin: <code>admin</code> / <code>admin123</code></p>
                        </div>

                        <div className="text-center mt-3">
                            <small className="text-muted">
                                Don't have an account?{' '}
                                <Link to="/register" style={{ color: 'var(--primary)', fontWeight: '600', textDecoration: 'none' }}>
                                    Create one here
                                </Link>
                            </small>
                        </div>
                    </Card.Body>
                </Card>
            </Container>
        </div>
    );
};

export default Login;
