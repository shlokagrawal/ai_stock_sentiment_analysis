import React from 'react';
import { render, screen } from '@testing-library/react';
import Footer from './Footer';
beforeAll(() => {
    jest.spyOn(console, 'error').mockImplementation((msg) => {
      if (!msg.includes('ReactDOMTestUtils.act')) {
        console.error(msg);
      }
    });
  });
  
// Mock current year for predictable testing (optional but good practice)
const currentYear = new Date().getFullYear();

describe('Footer Component', () => {
  test('renders footer with current year', () => {
    render(<Footer />);

    // Check for year
    expect(screen.getByText(new RegExp(currentYear.toString()))).toBeInTheDocument();

    // Check for the link text
    const link = screen.getByRole('link', { name: /stock sentiment analysis/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/');

    // Check for full sentence (partial match)
    expect(screen.getByText(/AI-Driven Stock Sentiment Analysis/i)).toBeInTheDocument();
  });
});
