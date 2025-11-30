import { supabase } from '../lib/supabaseClient';

export const favoriteService = {
    async getFavorites(userId: string): Promise<string[]> {
        const { data, error } = await supabase
            .from('favorites')
            .select('job_id')
            .eq('user_id', userId);
        if (error) throw error;
        return data?.map(fav => fav.job_id) || [];
    },

    async addFavorite(userId: string, jobId: string): Promise<void> {
        const { error } = await supabase
            .from('favorites')
            .insert([{ user_id: userId, job_id: jobId }]);

        if (error) throw error;
    },

    async removeFavorite(userId: string, jobId: string): Promise<void> {
        const { error } = await supabase
            .from('favorites')
            .delete()
            .eq('user_id', userId)
            .eq('job_id', jobId);

        if (error) throw error;
    },

    async toggleFavorite(userId: string, jobId: string, isFavorite: boolean): Promise<void> {
        if (isFavorite) {
            await this.removeFavorite(userId, jobId);
        } else {
            await this.addFavorite(userId, jobId);
        }
    }
};