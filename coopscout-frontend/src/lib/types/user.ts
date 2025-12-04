export interface User {
    id: string;
    email: string;
    full_name: string | null;
    major: string | null;
    gpa: number | null;
    graduation_year: number | null;
    created_at: string;
    updated_at: string;
}

export interface UserFormData {
    full_name: string;
    major: string;
    graduation_year: string;
    gpa: string;
}