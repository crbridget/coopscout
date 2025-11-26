import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export async function getUserProfile(user_id: int) {
    const {data, error } = await supabase
        .from('User')
        .select()
        .eq('user_id', user_id)

    if (error) console.error('Error fetching user:', error)
    return data
}