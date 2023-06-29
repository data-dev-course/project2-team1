import React from 'react';
import { renderHook } from "@testing-library/react";
import { getTotalDoc } from 'src/loader/postDataLoader';
import  { QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

const queryClient = new QueryClient();
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

const { result, waitFor } = renderHook(() => getTotalDoc(), { wrapper });

await waitFor(() => {
  return result.current.isSuccess;
});

expect(result.current.data).toGreaterThan(100);