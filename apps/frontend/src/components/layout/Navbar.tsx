import { Link } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { logout } from '../../store/authSlice';
import { api } from '../../store/api';
import { Button } from '../ui/Button';

export default function Navbar() {
    const { username, role, token } = useAppSelector((s) => s.auth);
    const dispatch = useAppDispatch();

    const handleLogout = async () => {
        try {
            await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'}/api/auth/logout`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
        } catch {
            // Proceed with client-side logout even if server call fails
        }
        dispatch(api.util.resetApiState());
        dispatch(logout());
    };

    return (
        <nav className="sticky top-0 z-50 backdrop-blur-xl bg-surface/80 border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-primary/25 group-hover:shadow-primary/40 transition-shadow">
                            S
                        </div>
                        <span className="text-xl font-semibold bg-gradient-to-r from-primary-light to-accent bg-clip-text text-transparent">
                            Smart Catalog
                        </span>
                    </Link>

                    <div className="flex items-center gap-4">
                        {username ? (
                            <>
                                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-lighter/60 border border-white/5">
                                    <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                                    <span className="text-sm text-text-muted">{username}</span>
                                    {role === 'ADMIN' && (
                                        <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-accent/20 text-accent">
                                            Admin
                                        </span>
                                    )}
                                </div>
                                <Button variant="secondary" size="sm" onClick={handleLogout}>
                                    Logout
                                </Button>
                            </>
                        ) : (
                            <Link to="/login">
                                <Button size="sm">
                                    Sign In
                                </Button>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
