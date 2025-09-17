import React, { useState } from 'react';
import { authService } from '../services/auth';
import type { RegisterRequest } from '../services/auth';
import './AuthPage.css';

interface SignupFormProps {
  onSwitchToLogin: () => void;
  onSignupSuccess: () => void;
}

const SignupForm: React.FC<SignupFormProps> = ({ onSwitchToLogin, onSignupSuccess }) => {
  const [formData, setFormData] = useState<RegisterRequest>({
    name: '',
    email: '',
    number: '',
    password: '',
    door_no: '',
    street: '',
    city: '',
    state: '',
    zipcode: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState<1 | 2>(1);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  // Validate fields depending on the current step
  const validateStep = (currentStep: 1 | 2): string | null => {
    if (currentStep === 1) {
      if (!formData.name || !formData.email || !formData.number || !formData.password) {
        return 'Please fill in all required fields';
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        return 'Please enter a valid email address';
      }

      // Phone number validation
      const phoneRegex = /^\d{10}$/;
      if (!phoneRegex.test(formData.number)) {
        return 'Phone number must be 10 digits';
      }

      // Password validation (simplified - only length requirement)
      if (formData.password.length < 8) {
        return 'Password must be at least 8 characters';
      }
      return null;
    }

    // Step 2 (address) validation
    if (!formData.door_no || !formData.street || !formData.city || !formData.state || !formData.zipcode) {
      return 'Please complete your address';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // If on step 1, validate and move to step 2 without submitting
    if (step === 1) {
      const validationError = validateStep(1);
      if (validationError) {
        setError(validationError);
        return;
      }
      setStep(2);
      return;
    }

    // Step 2: validate address and submit everything together
    const validationError = validateStep(2);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    try {
      await authService.register(formData);
      onSignupSuccess();
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.status === 400) {
        setError('Registration failed. Please check your information.');
      } else {
        setError('Registration failed. Please try again.');
      }
      console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="form-section">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        {step === 1 && (
          <>
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="tel"
              name="number"
              placeholder="Phone Number (10 digits)"
              value={formData.number}
              onChange={handleChange}
              disabled={isLoading}
              maxLength={10}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </>
        )}

        {step === 2 && (
          <>
            <input
              type="text"
              name="door_no"
              placeholder="Door Number"
              value={formData.door_no}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="text"
              name="street"
              placeholder="Street Address"
              value={formData.street}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="text"
              name="city"
              placeholder="City"
              value={formData.city}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="text"
              name="state"
              placeholder="State"
              value={formData.state}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            <input
              type="text"
              name="zipcode"
              placeholder="ZIP Code"
              value={formData.zipcode}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </>
        )}

        {error && <div className="error-message">{error}</div>}

        <div style={{ display: 'flex', gap: '12px', marginTop: '10px' }}>
          {step === 2 && (
            <button type="button" onClick={() => setStep(1)} disabled={isLoading} style={{ background: '#eee', color: '#333' }}>
              Back
            </button>
          )}
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating Account...' : step === 1 ? 'Continue' : 'Sign Up'}
          </button>
        </div>
      </form>
      <p>Already have an account? <a href="#" onClick={onSwitchToLogin}>Login</a></p>
    </div>
  );
};

export default SignupForm;
