import { createClient } from '@supabase/supabase-js';
import type { Database } from './types';

const SUPABASE_URL = "https://pkefwvvkydzzfstzwppv.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZWZ3dnZreWR6emZzdHp3cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDczNDI2NzUsImV4cCI6MjA2MjkxODY3NX0.ACpmG9nW2riQTsNZznHviEMNCcRr1KlaXfMfFpq4ps4";

// Import the supabase client like this:
// import { supabase } from "@/integrations/supabase/client";

export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);