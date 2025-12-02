import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://pykydgynnqjyxgvqjmws.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5a3lkZ3lubnFqeXhndnFqbXdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2MzA3MTcsImV4cCI6MjA4MDIwNjcxN30.cwqchjrJ4o6PtARWeC-Z9vOMrjX9JRNRv_w_I0YHkE0';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);