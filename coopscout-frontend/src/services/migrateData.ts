import { supabase } from '../src/lib/supabaseClient';
import jobsData from '../public/coopsearch.json';

async function migrateJobs() {
    const { data, error } = await supabase
        .from('jobs')
        .insert(jobsData);

    if (error) {
        console.error('Error migrating jobs:', error);
    } else {
        console.log('Successfully migrated jobs!', data);
    }
}

migrateJobs();