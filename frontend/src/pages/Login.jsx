import React, { useState, useContext } from 'react';
import { Form, Button, Container, Card } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(username, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center mt-5" style={{ minHeight: '60vh' }}>
            <Card className="premium-card p-4 hover-scale" style={{ width: '400px' }}>
                <Card.Body>
                    <h2 className="text-center mb-4" style={{ color: 'var(--primary)', fontWeight: 'bold' }}>Welcome Back</h2>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Username</Form.Label>
                            <Form.Control 
                                type="text" 
                                placeholder="Enter username" 
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required 
                            />
                        </Form.Group>
                        <Form.Group className="mb-4">
                            <Form.Label>Password</Form.Label>
                            <Form.Control 
                                type="password" 
                                placeholder="Password" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required 
                            />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100" style={{ backgroundColor: 'var(--primary)', border: 'none' }}>
                            Login
                        </Button>
                    </Form>
                    <div className="text-center mt-3">
                        <small className="text-muted">Don't have an account? <Link to="/register" style={{ color: 'var(--primary)' }}>Register here</Link></small>
                    </div>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default Login;
