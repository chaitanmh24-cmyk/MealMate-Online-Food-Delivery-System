import React, { useContext } from 'react';
import { Navbar, Nav, Container, Button, Badge } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const NavbarComponent = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [darkMode, setDarkMode] = React.useState(false);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
        if (!darkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    };

    return (
        <Navbar expand="lg" className="navbar-custom sticky-top shadow-sm py-2">
            <Container>
                <Navbar.Brand as={Link} to="/" className="d-flex align-items-center gap-2" style={{ fontWeight: '800', fontSize: '1.4rem', color: 'var(--primary)' }}>
                    <span>🍔</span> <span>MealMate</span>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto ms-3">
                        <Nav.Link as={Link} to="/" className="fw-semibold">🏠 Home</Nav.Link>
                    </Nav>
                    <Nav className="align-items-center gap-2">
                        <Button 
                            variant="light" 
                            onClick={toggleDarkMode} 
                            className="rounded-circle p-2 border-0" 
                            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                            style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        >
                            {darkMode ? '☀️' : '🌙'}
                        </Button>

                        {user ? (
                            <>
                                {user.role === 'Admin' ? (
                                    <Nav.Link 
                                        as={Link} 
                                        to="/admin" 
                                        className="btn btn-sm btn-outline-danger fw-bold px-3 me-1 text-danger"
                                        style={{ borderRadius: '20px' }}
                                    >
                                        ⚙️ Admin Dashboard
                                    </Nav.Link>
                                ) : (
                                    <Nav.Link 
                                        as={Link} 
                                        to="/cart" 
                                        className="fw-bold px-3 me-1 position-relative"
                                    >
                                        🛒 Cart
                                    </Nav.Link>
                                )}

                                <Nav.Link as={Link} to="/dashboard" className="d-flex align-items-center gap-1 fw-semibold">
                                    <span>👤</span>
                                    <span>{user.username}</span>
                                    <Badge bg={user.role === 'Admin' ? 'danger' : 'primary'} className="ms-1" style={{ fontSize: '0.7rem' }}>
                                        {user.role}
                                    </Badge>
                                </Nav.Link>

                                <Button 
                                    variant="outline-secondary" 
                                    size="sm" 
                                    onClick={handleLogout} 
                                    className="ms-2 px-3 fw-semibold"
                                    style={{ borderRadius: '20px' }}
                                >
                                    🚪 Logout
                                </Button>
                            </>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login" className="fw-semibold px-3">
                                    Sign In
                                </Nav.Link>
                                <Button 
                                    as={Link} 
                                    to="/register" 
                                    className="fw-bold px-4 shadow-sm" 
                                    style={{ backgroundColor: 'var(--primary)', borderColor: 'var(--primary)', borderRadius: '20px' }}
                                >
                                    Register
                                </Button>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default NavbarComponent;
