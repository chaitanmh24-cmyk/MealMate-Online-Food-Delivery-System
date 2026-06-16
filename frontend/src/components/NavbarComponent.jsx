import React, { useContext } from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
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
        <Navbar expand="lg" className="navbar-custom sticky-top">
            <Container>
                <Navbar.Brand as={Link} to="/" style={{ fontWeight: 'bold', color: 'var(--primary)' }}>
                    🍔 MealMate
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link as={Link} to="/">Home</Nav.Link>
                    </Nav>
                    <Nav className="align-items-center">
                        <Button variant="link" onClick={toggleDarkMode} className="text-decoration-none fs-5 me-2" style={{ color: 'var(--text)' }}>
                            {darkMode ? '☀️' : '🌙'}
                        </Button>
                        {user ? (
                            <>
                                {user.role === 'Admin' && <Nav.Link as={Link} to="/admin" style={{ color: 'var(--primary)', fontWeight: 'bold' }}>Admin Dashboard</Nav.Link>}
                                <Nav.Link as={Link} to="/cart">Cart</Nav.Link>
                                <Nav.Link as={Link} to="/dashboard">Dashboard ({user.username})</Nav.Link>
                                <Button variant="outline-danger" onClick={handleLogout} className="ms-2">Logout</Button>
                            </>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                                <Button variant="primary" as={Link} to="/register" className="ms-2" style={{ backgroundColor: 'var(--primary)', border: 'none' }}>Register</Button>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default NavbarComponent;
