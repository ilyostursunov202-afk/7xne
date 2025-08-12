import React, { useState } from 'react';
import axios from 'axios';
import { Star, MessageCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { Avatar, AvatarFallback } from './ui/avatar';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const ReviewForm = ({ productId, onReviewSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      setError('Please login to leave a review');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      await api.post(`/api/products/${productId}/reviews`, {
        product_id: productId,
        rating,
        comment
      });
      
      setRating(5);
      setComment('');
      onReviewSubmitted();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <Alert>
        <AlertDescription>Please login to leave a review.</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Write a Review</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="rating">Rating</Label>
            <div className="flex items-center space-x-2 mt-1">
              {[...Array(5)].map((_, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setRating(i + 1)}
                  className="focus:outline-none hover:scale-110 transition-transform"
                >
                  <Star
                    className={`h-6 w-6 ${
                      i < rating 
                        ? 'text-yellow-400 fill-current' 
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
              <span className="text-sm text-gray-600 ml-2">{rating} star{rating !== 1 ? 's' : ''}</span>
            </div>
          </div>

          <div>
            <Label htmlFor="comment">Review</Label>
            <Textarea
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Share your experience with this product..."
              rows="3"
              required
              className="mt-1"
            />
          </div>

          {error && (
            <Alert>
              <AlertDescription className="text-red-600">{error}</AlertDescription>
            </Alert>
          )}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Submitting...' : 'Submit Review'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export const ReviewList = ({ reviews }) => {
  if (!reviews || reviews.length === 0) {
    return (
      <div className="text-center py-8">
        <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No reviews yet. Be the first to review this product!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <Card key={review.id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>{review.user_name?.charAt(0)?.toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium text-sm">{review.user_name}</p>
                  <div className="flex items-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-3 w-3 ${
                          i < review.rating 
                            ? 'text-yellow-400 fill-current' 
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(review.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-gray-700">{review.comment}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};