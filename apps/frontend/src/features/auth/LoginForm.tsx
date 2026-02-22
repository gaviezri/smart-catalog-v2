import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLoginMutation } from '../../store/api';
import { useAppDispatch } from '../../store/hooks';
import { setCredentials } from '../../store/authSlice';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

export default function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [login, { isLoading, error }] = useLoginMutation();
    const dispatch = useAppDispatch();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const user = await login({ username, password }).unwrap();
            dispatch(setCredentials(user));
            navigate('/');
        } catch {
            // Error is handled by RTK Query state
        }
    };

    return (
        <div className="w-full max-w-md p-8 rounded-2xl bg-surface-light/30 border border-white/5 backdrop-blur-xl shadow-2xl">
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                    Welcome Back
                </h2>
                <p className="text-text-muted mt-2 text-sm">Sign in to manage your catalog</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <Input
                    label="Username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    required
                />

                <Input
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                />

                {error && (
                    <div className="p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-sm text-center">
                        Invalid username or password
                    </div>
                )}

                <Button
                    type="submit"
                    isLoading={isLoading}
                    className="w-full shadow-xl shadow-primary/20"
                >
                    Sign In
                </Button>
            </form>
        </div>
    );
}
