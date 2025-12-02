import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { theme } from '../../constants/theme';
import { Event, DEFAULT_EVENT_IMAGE } from '../../types';
import { supabase } from '../../services/supabase';

const { width } = Dimensions.get('window');
const RECENT_CARD_WIDTH = (width - 80) / 3;

export default function ProfileScreen() {
  const router = useRouter();
  const [recentEvents, setRecentEvents] = useState<Event[]>([]);
  const [quickAddEvents, setQuickAddEvents] = useState<Event[]>([]);
  const [bookmarkedEvents, setBookmarkedEvents] = useState<Set<string>>(new Set());
  const [checkedEvents, setCheckedEvents] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10);

      if (error) throw error;

      if (data) {
        setRecentEvents(data.slice(0, 3));
        setQuickAddEvents(data.slice(0, 5));
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const handleEventPress = (event: Event) => {
    router.push({
      pathname: '/event/[id]',
      params: { id: event.id, eventData: JSON.stringify(event) },
    });
  };

  const toggleBookmark = (eventId: string) => {
    setBookmarkedEvents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const toggleCheck = (eventId: string) => {
    setCheckedEvents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.settingsButton}>
            <Ionicons name="settings-outline" size={24} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.profileImageContainer}>
            <Image
              source={{ uri: 'https://i.pravatar.cc/300?img=1' }}
              style={styles.profileImage}
            />
            <TouchableOpacity style={styles.editButton}>
              <Ionicons name="pencil" size={16} color={theme.colors.white} />
            </TouchableOpacity>
          </View>

          <Text style={styles.name}>jeje</Text>
          <Text style={styles.handle}>@jejeruswan</Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="bookmark" size={24} color={theme.colors.white} />
            <Text style={styles.actionButtonText}>Saved</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="location" size={24} color={theme.colors.white} />
            <Text style={styles.actionButtonText}>Went</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="heart" size={24} color={theme.colors.white} />
            <Text style={styles.actionButtonText}>Liked</Text>
          </TouchableOpacity>
        </View>

        {/* Recent Views */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Recent Views</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.recentList}
          >
            {recentEvents.map((event) => (
              <TouchableOpacity
                key={event.id}
                style={styles.recentCard}
                onPress={() => handleEventPress(event)}
              >
                <Image
                  source={{ uri: event.image_url || DEFAULT_EVENT_IMAGE }}
                  style={styles.recentImage}
                />
                <Text style={styles.recentTitle} numberOfLines={2}>
                  {event.title}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Quick Add */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Add</Text>
          <View style={styles.quickAddList}>
            {quickAddEvents.map((event) => (
              <View key={event.id} style={styles.quickAddItem}>
                <Image
                  source={{ uri: event.image_url || DEFAULT_EVENT_IMAGE }}
                  style={styles.quickAddImage}
                />
                <View style={styles.quickAddInfo}>
                  <Text style={styles.quickAddTitle} numberOfLines={1}>
                    {event.title}
                  </Text>
                  <Text style={styles.quickAddSubtitle} numberOfLines={1}>
                    {event.description || event.location}
                  </Text>
                </View>
                <View style={styles.quickAddActions}>
                  <TouchableOpacity
                    style={styles.quickAddButton}
                    onPress={() => toggleBookmark(event.id)}
                  >
                    <Ionicons
                      name={bookmarkedEvents.has(event.id) ? 'bookmark' : 'bookmark-outline'}
                      size={24}
                      color={theme.colors.primary}
                    />
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.quickAddButton}
                    onPress={() => toggleCheck(event.id)}
                  >
                    <Ionicons
                      name={checkedEvents.has(event.id) ? 'checkmark' : 'checkmark-outline'}
                      size={24}
                      color={theme.colors.primary}
                    />
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    paddingHorizontal: theme.spacing.lg,
    paddingTop: theme.spacing.sm,
  },
  settingsButton: {
    padding: theme.spacing.sm,
  },
  profileSection: {
    alignItems: 'center',
    paddingVertical: theme.spacing.xl,
  },
  profileImageContainer: {
    position: 'relative',
    marginBottom: theme.spacing.md,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: theme.colors.gray[200],
  },
  editButton: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: theme.colors.white,
  },
  name: {
    fontSize: theme.fontSize.xxl,
    fontFamily: 'Inter_700Bold',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.xs,
  },
  handle: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_400Regular',
    color: theme.colors.textSecondary,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.xl,
    marginBottom: theme.spacing.xxxl,
    gap: theme.spacing.md,
  },
  actionButton: {
    flex: 1,
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.lg,
    borderRadius: theme.borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtonText: {
    fontSize: theme.fontSize.sm,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.white,
    marginTop: theme.spacing.xs,
  },
  section: {
    marginBottom: theme.spacing.xxxl,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.textPrimary,
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  recentList: {
    paddingHorizontal: theme.spacing.lg,
    gap: theme.spacing.md,
  },
  recentCard: {
    width: RECENT_CARD_WIDTH,
    marginRight: theme.spacing.md,
  },
  recentImage: {
    width: RECENT_CARD_WIDTH,
    height: RECENT_CARD_WIDTH * 1.2,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.gray[200],
    marginBottom: theme.spacing.sm,
  },
  recentTitle: {
    fontSize: theme.fontSize.sm,
    fontFamily: 'Inter_500Medium',
    color: theme.colors.textPrimary,
  },
  quickAddList: {
    paddingHorizontal: theme.spacing.lg,
  },
  quickAddItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  quickAddImage: {
    width: 50,
    height: 50,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: theme.colors.gray[200],
    marginRight: theme.spacing.md,
  },
  quickAddInfo: {
    flex: 1,
    marginRight: theme.spacing.md,
  },
  quickAddTitle: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.xs,
  },
  quickAddSubtitle: {
    fontSize: theme.fontSize.sm,
    fontFamily: 'Inter_400Regular',
    color: theme.colors.textSecondary,
  },
  quickAddActions: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  quickAddButton: {
    padding: theme.spacing.xs,
  },
});