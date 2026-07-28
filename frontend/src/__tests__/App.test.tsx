import { test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders DocuMind title', () => {
  render(<App />);
  const titleElement = screen.getByRole('heading', { name: /DocuMind/i, level: 1 });
  expect(titleElement).toBeInTheDocument();
});

test('renders upload instructions', () => {
  render(<App />);
  const uploadText = screen.getByText(/Upload PDF Document/i);
  expect(uploadText).toBeInTheDocument();
});