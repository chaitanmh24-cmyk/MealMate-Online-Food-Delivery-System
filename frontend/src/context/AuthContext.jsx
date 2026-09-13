import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkUser = async () => {
            const token = localStorage.getItem('access');
            if (token) {
                try {
                    const decoded = jwtDecode(token);
                    // Optionally fetch profile from API
                    const res = await api.get('auth/profile/');
                    setUser(res.data);
                } catch (error) {
                    console.error("Invalid token", error);
                    localStorage.removeItem('access');
                    localStorage.removeItem('refresh');
                }
            }
            setLoading(false);
        };
        checkUser();
    }, []);

    const login = async (username, password) => {
        const res = await api.post('auth/login/', { username, password });
        localStorage.setItem('access', res.data.access);
        localStorage.setItem('refresh', res.data.refresh);
        let userData = res.data.user;
        if (!userData) {
            const profileRes = await api.get('auth/profile/');
            userData = profileRes.data;
        }
        setUser(userData);
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setUser(null);
    };

    const register = async (userData) => {
        await api.post('auth/register/', userData);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
