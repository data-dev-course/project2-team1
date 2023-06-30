import { render, screen } from '@testing-library/react';
import React from 'react';
import App from './App';
import {
    BrowserRouter,
} from "react-router-dom";

describe('App tests', () => {
    it('intro description', () => {
        render(<BrowserRouter><App /></BrowserRouter>);
        const heading = screen.getByText(/유기동물 공고 보기/i);
        expect(heading).toBeInTheDocument()
    });
});

//describe('Overview tests', () => {
//    it('intro description', () => {
//        render(<BrowserRouter><Overview /></BrowserRouter>);
//        const heading = screen.getByText(/보호 상태 분석/i);
//        expect(heading).toBeInTheDocument()
//    });
//});