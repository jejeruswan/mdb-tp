import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { theme } from '@/constants/theme';
import { Event, EventCategory, CATEGORIES } from '../../types';
import { supabase } from '../../services/supabase';
import { SearchBar } from '../../components/SearchBar';
import { CategoryChip } from '../../components/CategoryChip';
import { EventCard } from '../../components/EventCard';

export default function HomeScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<EventCategory | null>(null);
  const [trendingEvents, setTrendingEvents] = useState<Event[]>([]);
  const [allEvents, setAllEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);

      // Fetch all events, sorted by most recent
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      if (data) {
        // Trending = most recent 5 events
        setTrendingEvents(data.slice(0, 5));
        // All events
        setAllEvents(data);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchEvents();
  };

  const handleEventPress = (event: Event) => {
    router.push({
      pathname: '/event/[id]',
      params: { id: event.id, eventData: JSON.stringify(event) },
    });
  };

  const handleCategoryPress = (category: EventCategory) => {
    setSelectedCategory(selectedCategory === category ? null : category);
  };

  // Filter events based on search and category
  const filteredAllEvents = allEvents.filter((event) => {
    const matchesSearch = searchQuery
      ? event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.description?.toLowerCase().includes(searchQuery.toLowerCase())
      : true;

    const matchesCategory = selectedCategory
      ? event.category === selectedCategory
      : true;

    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Text style={styles.logo}>Bevents</Text>
        </View>

        {/* Search Bar */}
        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="recruitment"
        />

        {/* Trending Section */}
        {!searchQuery && !selectedCategory && trendingEvents.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Trending</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.trendingList}
            >
              {trendingEvents.map((event) => (
                <View key={event.id} style={styles.trendingCard}>
                  <EventCard
                    event={event}
                    onPress={() => handleEventPress(event)}
                    variant="featured"
                    showOrganization
                  />
                </View>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Category Filter */}
        <View style={styles.categorySection}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoryList}
          >
            {CATEGORIES.map((category) => (
              <CategoryChip
                key={category.id}
                emoji={category.emoji}
                label={category.label}
                isSelected={selectedCategory === category.id}
                onPress={() => handleCategoryPress(category.id)}
              />
            ))}
          </ScrollView>
        </View>

        {/* All Events Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>All Events</Text>
          {filteredAllEvents.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No events found</Text>
            </View>
          ) : (
            <View style={styles.grid}>
              {filteredAllEvents.map((event, index) => (
                <View
                  key={event.id}
                  style={index % 2 === 0 ? styles.gridItemLeft : styles.gridItemRight}
                >
                  <EventCard
                    event={event}
                    onPress={() => handleEventPress(event)}
                    variant="grid"
                  />
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Bottom padding for tab bar */}
        <View style={{ height: 100 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  header: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  logo: {
    fontSize: theme.fontSize.xxxl,
    fontFamily: 'Inter_700Bold',
    color: theme.colors.primary,
  },
  categorySection: {
    marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  categoryList: {
    paddingHorizontal: theme.spacing.lg,
  },
  section: {
    marginTop: theme.spacing.xl,
    marginBottom: theme.spacing.lg,
  },
  sectionTitle: {
    fontSize: theme.fontSize.xl,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.lg,
    paddingHorizontal: theme.spacing.lg,
  },
  trendingList: {
    paddingHorizontal: theme.spacing.lg,
  },
  trendingCard: {
    marginRight: theme.spacing.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: theme.spacing.lg,
  },
  gridItemLeft: {
    marginRight: theme.spacing.lg,
  },
  gridItemRight: {
    marginRight: 0,
  },
  emptyState: {
    paddingVertical: theme.spacing.xxxl,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_400Regular',
    color: theme.colors.textSecondary,
  },
});