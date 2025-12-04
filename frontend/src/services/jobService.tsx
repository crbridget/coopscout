import { supabase } from '../lib/supabaseClient';
import type { Job } from '../lib/types/job';

export const jobService = {
    async getAllJobs(): Promise<Job[]> {
        const { data, error } = await supabase
            .from('jobs')
            .select('*')
            .eq('status', 'active')
            .order('posted_date', { ascending: false });

        if (error) throw error;
        return data || [];
    },

    async addJob(job: Omit<Job, 'id'>): Promise<Job> {
        const { data, error } = await supabase
            .from('jobs')
            .insert([job])
            .select()
            .single();

        if (error) throw error;
        return data;
    }
};