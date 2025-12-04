import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://gjuvkricwrsdaqkyvfpk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqdXZrcmljd3JzZGFxa3l2ZnBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3OTQ2MDMsImV4cCI6MjA4MDM3MDYwM30._7Ds7pA7LsplHeZpx_bA7jro8e8AOSMh-GnIScq8ruQ';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);