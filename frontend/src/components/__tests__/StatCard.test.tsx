import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatCard } from '../StatCard';

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Files" value={42} accent="text-cyan-300" />);
    expect(screen.getByText('Files')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });
});
